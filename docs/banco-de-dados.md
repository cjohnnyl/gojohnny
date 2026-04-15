# Banco de Dados — GoJohnny

**Versão:** 0.2.0
**Data:** 2026-04-15  
**Status:** Atualizado com Supabase Auth e `runner_memory`

---

## Tabelas

### `runner_profiles`
Contexto central do corredor. É a fonte de verdade que alimenta todas as recomendações.

| Coluna | Tipo | Obrigatório | Descrição |
|--------|------|-------------|-----------|
| `user_id` | UUID FK | Sim | Referência ao usuário no Supabase Auth |
| `name` | TEXT | Sim | Nome do corredor |
| `level` | TEXT | Sim | `beginner` \| `intermediate` \| `advanced` |
| `weekly_volume_km` | REAL | Não | Volume semanal atual em km |
| `available_days_per_week` | INTEGER | Sim | Dias disponíveis por semana |
| `preferred_days` | TEXT | Não | Ex: `"seg,qua,sex"` |
| `comfortable_pace` | TEXT | Não | Pace confortável em min/km — ex: `"6:30"` |
| `main_goal` | TEXT | Não | `complete_5k` \| `complete_10k` \| `complete_21k` \| `improve_time` \| `consistency` \| `other` |
| `target_race_name` | TEXT | Não | Nome da prova alvo |
| `target_race_distance_km` | REAL | Não | Distância da prova alvo |
| `target_race_date` | TEXT | Não | Data ISO 8601 |
| `injury_history` | TEXT | Não | Histórico de lesões (texto livre) |
| `physical_limitations` | TEXT | Não | Limitações físicas atuais |
| `location` | TEXT | Não | Cidade/estado |
| `extra_context` | TEXT | Não | Contexto adicional livre |
| `created_at` | DATETIME | Sim | ISO 8601 |
| `updated_at` | DATETIME | Sim | ISO 8601 |

**Nota:** A coluna `user_id` é UUID e referencia usuários criados via Supabase Auth, não uma tabela local `users`.

**Campos mínimos para geração de planilha:**
`level`, `available_days_per_week`, `main_goal`

---

### `training_plans`
Planilhas semanais geradas pelo GoJohnny.

| Coluna | Tipo | Obrigatório | Descrição |
|--------|------|-------------|-----------|
| `id` | INTEGER PK | Sim | Identificador único |
| `user_id` | UUID FK | Sim | Referência ao usuário (Supabase Auth) |
| `week_start` | DATE | Sim | Segunda-feira da semana (YYYY-MM-DD) |
| `week_end` | DATE | Sim | Domingo da semana (YYYY-MM-DD) |
| `plan_data` | JSON | Sim | Lista de treinos por dia |
| `context_snapshot` | JSON | Não | Snapshot do perfil no momento da geração |
| `status` | TEXT | Sim | `active` \| `superseded` \| `archived` |
| `coach_notes` | TEXT | Não | Observações do treinador |
| `created_at` | DATETIME | Sim | Data de geração |
| `updated_at` | DATETIME | Sim | Última atualização |

**Estrutura de `plan_data`:**
```json
[
  {
    "day": "segunda",
    "type": "leve",
    "km": 5.0,
    "pace_sugerido": "6:30",
    "orientacoes": "Corrida leve em zona 2. Foco em manter conversa."
  },
  {
    "day": "quarta",
    "type": "intervalado",
    "km": 6.0,
    "pace_sugerido": "5:45",
    "orientacoes": "4x1000m no pace de prova com 90s de recuperação."
  }
]
```

---

### `training_feedbacks`
Feedback pós-treino. Informa as adaptações futuras da planilha e atualiza `runner_memory`.

| Coluna | Tipo | Obrigatório | Descrição |
|--------|------|-------------|-----------|
| `id` | INTEGER PK | Sim | Identificador único |
| `user_id` | UUID FK | Sim | Referência ao usuário (Supabase Auth) |
| `plan_id` | INTEGER FK | Não | Planilha relacionada |
| `training_date` | DATE | Sim | Data do treino (YYYY-MM-DD) |
| `effort_rating` | INTEGER | Não | 1-10 |
| `pain_level` | INTEGER | Não | 0-10 (usado para alertar em `runner_memory`) |
| `sleep_quality` | INTEGER | Não | 1-5 |
| `general_feeling` | TEXT | Não | `great` \| `good` \| `ok` \| `bad` \| `very_bad` |
| `notes` | TEXT | Não | Notas livres |
| `ai_analysis` | TEXT | Não | Análise gerada pelo GoJohnny |
| `load_recommendation` | TEXT | Não | `maintain` \| `reduce` \| `increase` |
| `created_at` | DATETIME | Sim | Data de criação |

---

### `conversations`
Sessões de chat com o GoJohnny.

| Coluna | Tipo | Obrigatório | Descrição |
|--------|------|-------------|-----------|
| `id` | INTEGER PK | Sim | Identificador único |
| `user_id` | UUID FK | Sim | Referência ao usuário (Supabase Auth) |
| `title` | TEXT | Não | Gerado automaticamente ou manual |
| `created_at` | DATETIME | Sim | Data de criação |
| `updated_at` | DATETIME | Sim | Última atividade |

---

### `messages`
Histórico de mensagens. Alimenta o contexto enviado à OpenAI API.

| Coluna | Tipo | Obrigatório | Descrição |
|--------|------|-------------|-----------|
| `id` | INTEGER PK | Sim | Identificador único |
| `conversation_id` | INTEGER FK | Sim | Referência à conversa |
| `role` | TEXT | Sim | `user` \| `assistant` |
| `content` | TEXT | Sim | Conteúdo da mensagem |
| `tokens_used` | INTEGER | Não | Tokens consumidos (controle de custo) |
| `model_used` | TEXT | Não | Modelo OpenAI usado (ex: `gpt-4o-mini`) |
| `created_at` | DATETIME | Sim | Timestamp da mensagem |

---

### `runner_memory`
Contexto dinâmico e memória de acompanhamento do corredor. Uma entrada por usuário, atualizada após feedbacks, mensagens e eventos.

| Coluna | Tipo | Obrigatório | Descrição |
|--------|------|-------------|-----------|
| `id` | INTEGER PK | Sim | Identificador único |
| `user_id` | UUID FK Unique | Sim | Referência ao usuário (Supabase Auth) |
| `active_plan_id` | INTEGER FK | Não | ID da planilha ativa |
| `plan_week_current` | INTEGER | Não | Semana atual (1-based) |
| `plan_week_total` | INTEGER | Não | Total de semanas do plano |
| `plan_started_at` | DATE | Não | Data de início do plano |
| `week_progress` | JSON | Não | Progresso semanal: `{"segunda": "done", "terça": "skipped", ...}` |
| `recent_feedbacks` | JSON | Não | Últimos 3 feedbacks: `[{"date": "...", "effort": 8, "pain": 3, "feeling": "good"}, ...]` |
| `physical_alerts` | JSON | Não | Alertas ativos: `[{"type": "high_pain", "location": "joelho", "noted_at": "..."}]` |
| `load_adjustments` | JSON | Não | Histórico de ajustes: `[{"date": "...", "recommendation": "reduce", "reason": "..."}]` |
| `chat_observations` | JSON | Não | Observações capturadas (máx 10): `[{"note": "treina melhor de manhã", "captured_at": "..."}]` |
| `last_coaching_style` | TEXT | Não | Estilo usado: `motivador` \| `técnico` \| `desafiador` \| `conservador` |
| `last_session_summary` | TEXT | Não | Resumo/notas da última sessão |
| `last_session_at` | DATETIME | Não | Timestamp da última sessão |
| `created_at` | DATETIME | Sim | Data de criação |
| `updated_at` | DATETIME | Sim | Última atualização |

**Uso:** Injetada como bloco de contexto no system prompt do chat (~200-250 tokens). Atualizada após cada feedback, novo plano ou sessão de chat.

Consulte **ADR-002** para detalhes sobre estratégia de memória útil.

---

## Mudanças em relação à versão 0.1.0

### Removido
- Tabela `users` (usuários agora gerenciados por Supabase Auth)
- Coluna `password_hash` em qualquer tabela

### Modificado
- Campo `user_id` de `INTEGER` para `UUID` em:
  - `runner_profiles`
  - `training_plans`
  - `training_feedbacks`
  - `conversations`
  - `runner_memory` (nova)

- Tipo de datas:
  - `TEXT (ISO 8601)` → `DATE` ou `DATETIME` (depende da precisão necessária)

- Modelos de IA:
  - Claude (Anthropic) → OpenAI GPT (`gpt-4o-mini`, `gpt-4o`)

### Adicionado
- Tabela `runner_memory` (contexto dinâmico)
- Coluna `id` PK em tabelas sem ele
- Timestamps `created_at` e `updated_at` em tabelas transacionais

---

## Estratégia de evolução do schema

1. Toda mudança de schema deve ser uma migration Alembic numerada
2. Nunca alterar colunas existentes diretamente — adicionar novas colunas nullable
3. `extra_context` em `runner_profiles` absorve campos temporários durante exploração
4. `context_snapshot` em `training_plans` preserva rastreabilidade mesmo após updates no perfil
5. `runner_memory` é a ponte entre dados transacionais e contexto injetado no LLM
6. Tabelas futuras previstas: `race_registrations`, `strava_integrations`, `user_preferences`, `achievements`
