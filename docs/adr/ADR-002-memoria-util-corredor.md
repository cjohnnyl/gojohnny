# ADR-002 — Estratégia de Memória Útil do Corredor

**Data:** 2026-04-15  
**Status:** Aceito  
**Autores:** talita-ai-specialist, aline-backend-engineer, mateus-architect-techlead

---

## Contexto

O chatbot do GoJohnny fornecia recomendações baseado no **perfil estático** do corredor (nível, objetivo, histórico de lesões, etc.).

Problema: sem memória dinâmica, cada nova conversa iniciava do zero. O bot não conseguia acompanhar:
- O **plano em andamento** e qual semana o corredor está
- **Progresso semanal** (quantos treinos foram cumpridos)
- **Histórico recente de feedbacks** (últimas 3 semanas de dor, esforço, sensação)
- **Alertas físicos** (dor no joelho desde ontem, cansaço anormal)
- **Ajustes de carga** já aplicados (recomendação de redução de volume na semana passada)
- **Observações do chat anterior** (treina melhor de manhã, clima frio não combina com ele)

Consequência: o diferencial do produto — **coaching conversacional que acompanha o corredor semana a semana** — não podia ser realizado.

---

## Opções Avaliadas

### A. Memória integrada no modelo (context window)
Padrão: carrega histórico COMPLETO de mensagens no contexto do LLM.

**Prós:**
- Simples de implementar

**Contras:**
- Ineficiente (tokens gastos desnecessariamente)
- Limitado pelo context window (~4k–8k tokens em modelos baratos)
- Caro em modelos maiores (claude-sonnet custa 3x mais que gpt-4o-mini)
- Não sobrevive a mudanças de modelo

**Custo:** Amortizado em todas as requests

---

### B. Base de dados transacional + resumo manual
Padrão: salvar mensagens brás, resumir manualmente.

**Prós:**
- Total controle

**Contras:**
- Requer dois LLM calls: um para resumir, outro para responder
- Duplicação de estado (banco transacional + summarized context)

**Custo:** +1 call ao LLM por mensagem

---

### C. Tabela `runner_memory` — estado compacto, injetado dinâmico no prompt
Padrão: manter estrutura JSON com últimos 3 feedbacks, alertas ativos, plano em andamento, observações capturadas. Injetar como seção do system prompt.

**Prós:**
- Contexto reduzido (~250 tokens)
- Sobrevive a mudanças de modelo
- Atualizável via lógica de negócio (não precisa LLM para resumir)
- Preparado para escala (índices simples em `user_id`)

**Contras:**
- Requer schema novo e lógica de atualização
- Observações precisam ser capturadas explicitamente

---

## Decisão

**Opção C: Nova tabela `runner_memory` com contexto dinâmico injetado**

Implementação:
1. Nova tabela `runner_memory` no banco (um registro por usuário)
2. Função `build_dynamic_context_block(memory: RunnerMemory) -> str` injeta dados no system prompt
3. Lógica de negócio atualiza `runner_memory` após feedbacks, mensagens e eventos
4. Contexto dinâmico ≤ 250 tokens / requisição (target)

---

## Schema da Tabela `runner_memory`

```sql
CREATE TABLE runner_memory (
    id INTEGER PRIMARY KEY,
    user_id UUID UNIQUE NOT NULL,
    
    -- Estado do plano
    active_plan_id INTEGER,
    plan_week_current INTEGER,
    plan_week_total INTEGER,
    plan_started_at DATE,
    
    -- Progresso semanal
    week_progress JSONB,  -- {"segunda": "done", "terça": "skipped", ...}
    
    -- Histórico compacto
    recent_feedbacks JSONB,  -- Últimos 3 feedbacks: [{"date": "...", "effort": 8, "pain": 3, ...}]
    
    -- Alertas e ajustes
    physical_alerts JSONB,   -- [{"type": "high_pain", "location": "joelho", "noted_at": "..."}]
    load_adjustments JSONB,  -- [{"date": "...", "recommendation": "reduce", "reason": "..."}]
    
    -- Observações do chat
    chat_observations JSONB, -- [{"note": "treina melhor de manhã", "captured_at": "..."}] — máx 10
    
    -- Contexto da última sessão
    last_coaching_style VARCHAR(20),  -- motivador | técnico | desafiador | conservador
    last_session_summary TEXT,
    last_session_at DATETIME,
    
    -- Rastreamento
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_runner_memory_user_id ON runner_memory(user_id);
```

---

## O que entra em `runner_memory`

### ✅ ENTRA
- Semana atual do plano (numérico)
- Treinos completados / pulados / pendentes desta semana
- **Últimos 3 feedbacks:** esforço, dor, sono, sensação
- **Alertas ativos:** dor articular, fadiga, mal-estar
- **Ajustes de carga:** "reduzir 20%" aplicados na última semana
- **Observações capturadas:** "treina melhor de manhã", "prefere trilha"
- **Estilo de coaching usado:** para manter continuidade

### ❌ NÃO ENTRA
- Detalhes completos de treinos (estão em `training_plans`)
- Histórico de chat anterior (está em `messages`)
- Perfil do usuário (está em `runner_profiles` — imutável)
- Dados sensíveis de privacidade além do necessário

---

## Como é injetado no prompt

Função `build_dynamic_context_block(memory: RunnerMemory) -> str` retorna algo como:

```
--- CONTEXTO DINÂMICO DA SEMANA ---
Plano atual: Semana 3 de 12 (Corrida Longa — preparação para meia-maratona)
Progresso esta semana: segunda (ok) | terça (pulou) | quarta (ok) | quinta (?) | sexta (?) | sábado (?) | domingo (?)

Últimos feedbacks:
- seg 14-04: esforço 7/10, dor joelho 4/10, sono 7/10 → sensação: boa
- dom 13-04: esforço 8/10, dor 2/10, sono 8/10 → sensação: ótima
- sab 12-04: esforço 6/10, dor 0/10, sono 6/10 → sensação: boa

Alertas ativos:
- Dor no joelho (moderada) desde 14-04 → não piorou, continuar monitando

Observações capturadas:
- Treina melhor de manhã (cedo, 6h)
- Rota de 5km por Imirim é favorita
- Prefere companhia em corridas longas

Último ajuste: Semana 3 carga reduzida 10% por sono irregular na semana 2
Estilo de coaching: Motivador com técnica
--- FIM DO CONTEXTO DINÂMICO ---
```

Tamanho: ~200–250 tokens. Junta-se ao contexto estático (perfil) e permite LLM reconhecer estado completo do corredor.

---

## Lógica de Atualização

### Quando atualizar `runner_memory`?

1. **Após novo feedback** (`POST /feedback`):
   - Adiciona à `recent_feedbacks` (manter últimos 3)
   - Se `pain_level` > 6: adiciona alerta em `physical_alerts`
   - Se alerta resolve: remove de `physical_alerts`

2. **Após nova mensagem no chat** (`POST /chat/message`):
   - Se LLM detectar observação útil (via extração): adiciona a `chat_observations` (máx 10)
   - Exemplo: "Você mencionou que treina melhor de manhã" → captura automaticamente

3. **Após plano gerado** (`POST /plans`):
   - Atualiza `active_plan_id`, `plan_week_current`, `plan_week_total`, `plan_started_at`
   - Zera `week_progress` (semana recém-iniciada)

4. **Ao validar progresso semanal** (logic triggered por cron ou endpoint):
   - Atualiza `week_progress` com base em entregas de feedback

5. **Ao aplicar ajuste de carga** (automático via rules):
   - Adiciona em `load_adjustments`

### Frequência
- `runner_memory` é leitura frequente (cada chat message)
- Atualização é infrequente (feedback, novo plano, cron diário)

---

## Consequências

### Positivas
- Chat agora tem contexto dinâmico de acompanhamento
- Recomendações são personalizadas à semana em andamento
- Reduz token overhead (vs carregar histórico completo)
- Preparado para escala (índices simples)

### Negativas
- Novo schema + lógica de atualização
- Observações precisam ser capturadas via LLM ou manualmente (overhead leve)
- Se `runner_memory` ficar inconsistente com realidade, pode gerar contexto errado

### Mitigation de inconsistência
- `updated_at` registra última atualização
- Função `sync_runner_memory(user_id)` pode reconstruir a partir de dados transacionais (backup)
- Alertas resolvidos têm date e podem expirar automaticamente

---

## Validação

- [ ] Tabela `runner_memory` criada com schema correto
- [ ] Teste: criar usuário → feedback → verifique `recent_feedbacks` preenchido
- [ ] Teste: chat com `runner_memory` presente vs ausente — resposta difere?
- [ ] Teste: alerta físico capturado em feedback aparece em `physical_alerts`
- [ ] Teste: observação do chat capturada aparece em `chat_observations`
- [ ] Teste: `build_dynamic_context_block()` não ultrapassa 300 tokens

---

## Próximos passos

- **ADR-003 (futuro):** Extração automática de observações do chat (usar segundo LLM call menor para não impactar latência)
- **ADR-004 (futuro):** Resolução automática de alertas físicos por tempo (ex: dor de 4 dias atrás resolve automaticamente)
