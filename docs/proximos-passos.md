# Próximos Passos — GoJohnny

**Data:** 2026-04-15  
**Status:** Pós-MVP — Roadmap evolutivo

---

## Resumo do que foi feito (Operação V2)

Nesta operação, o GoJohnny passou por uma evolução significativa focada em **diferenciação competitiva** (coaching conversacional com memória) e **redução de overhead técnico** (auth delegada).

### Concluído

**Arquitetura:**
- [ ] ADR-001: Migração para Supabase Auth (delegada, segura)
- [ ] ADR-002: Estratégia de `runner_memory` para contexto dinâmico
- [ ] Mudança de IA: Anthropic Claude → OpenAI GPT (alinhado com código existente)

**Implementação Backend:**
- [ ] Novo modelo `RunnerMemory` com schema JSON compacto
- [ ] Função `build_dynamic_context_block()` injeta contexto no prompt
- [ ] Remoção de rotas `/auth/register` e `/auth/login` (migradas para Supabase)
- [ ] Atualização de schemas para `user_id: UUID`
- [ ] Middleware FastAPI para validação de JWT Supabase

**Implementação Frontend:**
- [ ] Integração Supabase Auth Client (email + senha)
- [ ] UI de login/signup integrada
- [ ] User menu com logout
- [ ] Onboarding conversacional (integrado ao chat, não formulário separado)
- [ ] Chat UI conecta ao backend com JWT

**Documentação:**
- [ ] ADR-001 e ADR-002 registram decisões
- [ ] Schema de banco atualizado com `runner_memory`
- [ ] Variáveis de ambiente documentadas (dev, staging, prod)
- [ ] Checklist de publicação pronto para primeiro deploy

**Validação (Patrícia):**
- [ ] Critérios de aceite passam
- [ ] Testes de integração backend + frontend validam fluxo completo
- [ ] Zero P1/P2 em aberto

---

## Etapas seguintes — Roadmap evolutivo

### **Fase 1 — Go Live (semana 1)**

**Objetivo:** Publicar MVP e validar hipótese com usuários reais.

**Tasks:**
- [ ] Seguir checklist de publicação (`docs/checklist-publicacao.md`)
- [ ] Deploy em Railway (backend) + Vercel (frontend)
- [ ] Configurar Supabase com RLS e backup automático
- [ ] Monitorar logs e performance iniciais
- [ ] Recolher feedback direto de usuários (max 5–10 beta users)

**Métricas:**
- Tempo de resposta do chat < 5s
- Taxa de erro < 0.1%
- Usuarios conseguem fazer login, preencher perfil, iniciar chat

**Risco:**
- Supabase Auth pode ter problemas com confirmação de email em staging
- JWT expiration pode causar logout inesperado
- Rate limiting da OpenAI pode ser atingido rapidamente

**Owner:** Thiago (DevOps) + Camila (Product)

---

### **Fase 2 — Observabilidade e Ajustes (semana 2)**

**Objetivo:** Entender padrões reais de uso, corrigir bugs, otimizar performance.

**Tasks:**
- [ ] Configurar Sentry ou similar para error tracking
- [ ] Adicionar métricas de uso:
  - Mensagens por usuário (média, distribuição)
  - Tempo de resposta do LLM (p50, p95, p99)
  - Tokens consumidos (para FinOps)
  - Taxa de churn (usuários que param de usar)
- [ ] Analisar logs das primeiras semanas
- [ ] Fazer hotfixes para bugs encontrados em produção
- [ ] Reanalisar custo de tokens (pode estar acima do budget?)

**Decisões esperadas:**
- Qual modelo OpenAI usar no chat real (gpt-4o-mini vs gpt-4o)?
- Precisa de rate limiting por usuário?
- Observações do chat precisam ser capturadas manualmente ou automaticamente?

**Owner:** Leandro (Data/Analytics) + Murilo (FinOps)

---

### **Fase 3 — Extração Automática de Observações (semana 3)**

**Objetivo:** Automatizar captura de insights do chat sem overhead de latência.

**Descrição:** Usar segundo LLM call (modelo menor, assíncrono) para extrair observações úteis do chat após a resposta principal.

Exemplo:
- Usuário: "Eu corro melhor de manhã, quando está mais fresco"
- Resposta do chat: "Ótimo! Treinos de manhã são ideais para volume..."
- Background: LLM extrair → capturar em `runner_memory.chat_observations`

**Tasks:**
- [ ] ADR-003: Estratégia de extração assíncrona de observações
- [ ] Implementar fila assíncrona (Celery + Redis ou async tasks)
- [ ] Criar função `extract_observations_from_message()`
- [ ] Testar latência (não deve impactar resposta do usuário)

**Owner:** Aline (Backend) + Talita (IA)

---

### **Fase 4 — Resolução Automática de Alertas (semana 4)**

**Objetivo:** Alertas físicos resolvem-se automaticamente após período de time.

**Descrição:** Se um alerta foi criado a 4 dias atrás e nenhum feedback novo confirmou permanência, remover de `physical_alerts`.

**Tasks:**
- [ ] ADR-004: Política de expiração de alertas
- [ ] Implementar cron job: `expire_old_alerts()` (executa todo dia)
- [ ] Testes: criar alerta, aguardar N dias, confirmar que expira

**Owner:** Aline (Backend)

---

### **Fase 5 — Planos Multissemanais (semana 5–6)**

**Objetivo:** Suportar planos que duram 4–12 semanas (para maratonas, por exemplo).

**Atualmente:**
- Plano gerado é sempre 1 semana
- Cada semana é um "reset"

**Mudanças necessárias:**

Schema:
- [ ] Adicionar coluna `plan_phases` em `training_plans` (estrutura JSON com fases do plano)
- [ ] Exemplo:
  ```json
  {
    "phases": [
      {
        "name": "Base building",
        "weeks": 1-4,
        "focus": "volume_low_intensity",
        "target_weekly_km": 20
      },
      {
        "name": "Intensidade",
        "weeks": 5-8,
        "focus": "speed_work",
        "target_weekly_km": 25
      },
      {
        "name": "Prova",
        "weeks": 9-12,
        "focus": "taper",
        "target_weekly_km": 15
      }
    ]
  }
  ```

Backend:
- [ ] Prompt do LLM incluir fase atual do plano
- [ ] Validação: não permitir intensidade fora de fase
- [ ] Feedback pode ajustar carga apenas da fase atual

UI Frontend:
- [ ] Visualizar fases do plano (gantt chart simples?)
- [ ] Permitir gerar plano com duração customizável

**Owner:** Camila (Product) + Mateus (Arquitetura) + Aline (Backend)

---

### **Fase 6 — Integração Strava (semana 7–8)**

**Objetivo:** Sincronizar dados de treino da Strava com GoJohnny.

**Descrição:** Usuário conecta conta Strava, e histórico de treinos é puxado automaticamente para contextualizar feedback e recomendações.

**Tasks:**
- [ ] Registrar app GoJohnny em Strava Developers
- [ ] Implementar OAuth 2.0 flow Strava
- [ ] Criar tabela `strava_integrations` (conexão de usuário)
- [ ] Sync diário de atividades mais recentes
- [ ] Extrair dados úteis (distância, pace médio, altitude) para feedback
- [ ] Integrar ao contexto dinâmico (`runner_memory`)

**API Strava:** https://developers.strava.com

**Owner:** Aline (Backend) + Thiago (DevOps/webhooks)

---

### **Fase 7 — Dashboard de Progresso (semana 9–10)**

**Objetivo:** UI que visualiza progresso do corredor ao longo de semanas.

**Elementos:**
- Gráfico de volume semanal (km/semana ao longo do tempo)
- Taxa de cumprimento do plano (treinos feitos / planejados)
- Evolução de sensações (feels, effort, pain) — heatmap ou linha temporal
- Próximas provas e countdown
- Metas e progresso

**Owner:** Caio (Frontend/UI) + Leandro (Data, se precisa de agregação de dados)

---

### **Fase 8 — Exportação de Plano/Chat (semana 11–12)**

**Objetivo:** Usuários conseguem exportar plano ou conversa para PDF/Excel.

**Tasks:**
- [ ] PDF: Plano semanal formatado bem
- [ ] Excel: Histórico de feedbacks e observações
- [ ] PDF: Conversa do chat com timestamps
- [ ] UI: botão "Download" em cada seção

**Owner:** Caio (Frontend) + Aline (Backend, endpoint de export)

---

### **Fase 9 — Sistema de Prêmios/Gamificação (semana 13–14)**

**Objetivo:** Motivar consistência com prêmios e badges.

**Elementos:**
- "7 days in a row" badge
- "50km weekly" achievement
- "Pace progression" badge (melhorou x% em Y semanas)

**Tasks:**
- [ ] Tabela `achievements` no banco
- [ ] Lógica para detectar quando achievements são ganhados
- [ ] UI para mostrar achievements no dashboard

**Owner:** Camila (Product) + Aline (Backend)

---

## Roadmap de curto prazo (2–4 semanas)

```
Semana 1: Go Live (Railway + Vercel)
          ↓
Semana 2: Observabilidade + Hotfixes
          ↓
Semana 3: Extração automática de observações
          ↓
Semana 4: Resolução automática de alertas
```

**Blocker crítico:** Nenhum. Podem ser feitos em paralelo.

## Roadmap de médio prazo (1–3 meses)

```
Semana 5–6:   Planos multissemanais
Semana 7–8:   Integração Strava
Semana 9–10:  Dashboard de progresso
Semana 11–12: Exportação de plano/chat
Semana 13–14: Gamificação
```

---

## Decisões não tomadas (backlog)

| Decisão | Contexto | Prioridade |
|---------|----------|-----------|
| **OAuth social (Google/Apple)** | Supabase suporta, mas MVP usa email puro | Baixa (pós-MVP) |
| **Notificações push** | Lembrar de completar treino? | Média (semanas 5–6) |
| **Integração Apple Health/Garmin** | Similar a Strava | Baixa |
| **Coaching de nutrição** | Fora do escopo MVP | Muito baixa |
| **Comunidade/leaderboards** | Gamificação social | Muito baixa |
| **Coach humano (video call)** | Escalabilidade questionável | Muito baixa |

---

## Métricas de sucesso (MVP)

- [ ] 10+ usuários ativos diários
- [ ] Tempo de resposta chat < 5s (p95)
- [ ] Taxa de churn < 20% (ao final de semana 2)
- [ ] Feedback positivo (CSAT > 7/10)
- [ ] Custo operacional < $100/mês

---

## Entregáveis desta fase

| Artefato | Status | Localização |
|----------|--------|------------|
| ADR-001 (Supabase Auth) | ✅ Concluído | `docs/adr/ADR-001-infraestrutura-supabase.md` |
| ADR-002 (Runner Memory) | ✅ Concluído | `docs/adr/ADR-002-memoria-util-corredor.md` |
| Schema atualizado | ✅ Concluído | `docs/banco-de-dados.md` |
| Variáveis de ambiente | ✅ Concluído | `docs/variaveis-de-ambiente.md` |
| Checklist de publicação | ✅ Concluído | `docs/checklist-publicacao.md` |
| Código backend | ✅ Concluído | `backend/` |
| Código frontend | ✅ Concluído | `frontend/` |
| Testes (Patrícia) | ✅ Concluído | Validação registrada |

---

## Comunicação com stakeholders

**Usuários:**
- "GoJohnny agora funciona com memória — lembra do seu progresso semana a semana"
- "Seu perfil, seus feedbacks, suas observações alimentam as recomendações"
- "Você está usando GPT (OpenAI), que oferece melhor contexto para corrida"

**Time técnico:**
- ADRs registram decisões para evitar re-discussões
- Próximas features tem owner claro e estimativa de tempo
- Fase de go-live pode ter surpresas — estar preparado

**Produto:**
- MVP pronto para launch com diferencial competitivo claro
- Feedback de usuários (semanas 1–2) vai informar prioridades
- Planos multissemanais são next big feature (valor alto, complexidade alta)

---

## Risco e Mitigation

| Risco | Probabilidade | Impacto | Mitigation |
|-------|---------------|--------|-----------|
| Custo OpenAI explode | Média | Alto | Rate limiting por usuário, usar gpt-4o-mini |
| Supabase Auth com problema | Baixa | Crítico | Ter plano B (Auth0 ativável em 1 dia) |
| Usuários não conseguem fazer signup | Média | Alto | Testes rigorosos antes de go-live |
| Chat muito lento (>10s) | Média | Médio | Otimizar prompt, usar modelo menor |
| Dados inconsistentes (runner_memory vs realidade) | Baixa | Médio | Função `sync_runner_memory()` de backup |

---

## Próximas reuniões

- [ ] **Reunião de kick-off go-live** (com Thiago, Camila) — revisar checklist
- [ ] **Retrospectiva pós-launch** (com todo time) — aprender com feedback real
- [ ] **Planning de Fase 2** (Leandro, Murilo, Mateus) — observabilidade e análise
