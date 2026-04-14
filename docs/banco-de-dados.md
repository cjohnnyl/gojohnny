# Banco de Dados — GoJohnny

**Versão:** 0.1.0
**Data:** 2026-04-13

---

## Tabelas

### `users`
Identidade e autenticação do corredor.

| Coluna | Tipo | Obrigatório | Descrição |
|--------|------|-------------|-----------|
| `id` | INTEGER PK | Sim | Identificador único |
| `email` | TEXT UNIQUE | Sim | Email de login |
| `password_hash` | TEXT | Sim | Hash bcrypt da senha |
| `is_active` | INTEGER | Sim | 1 = ativo, 0 = desativado |
| `created_at` | TEXT | Sim | ISO 8601 |
| `updated_at` | TEXT | Sim | ISO 8601 |

---

### `runner_profiles`
Contexto central do corredor. É a fonte de verdade que alimenta todas as recomendações.

| Coluna | Tipo | Obrigatório | Descrição |
|--------|------|-------------|-----------|
| `user_id` | INTEGER FK | Sim | Referência ao usuário |
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

**Campos mínimos para geração de planilha:**
`level`, `available_days_per_week`, `main_goal`

---

### `training_plans`
Planilhas semanais geradas pelo GoJohnny.

| Coluna | Tipo | Obrigatório | Descrição |
|--------|------|-------------|-----------|
| `user_id` | INTEGER FK | Sim | Referência ao usuário |
| `week_start` | TEXT | Sim | ISO 8601 — segunda-feira da semana |
| `week_end` | TEXT | Sim | ISO 8601 — domingo da semana |
| `plan_data` | TEXT (JSON) | Sim | Lista de treinos por dia |
| `context_snapshot` | TEXT (JSON) | Não | Snapshot do perfil no momento da geração |
| `status` | TEXT | Sim | `active` \| `superseded` \| `archived` |
| `coach_notes` | TEXT | Não | Observações do treinador |

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
Feedback pós-treino. Informa as adaptações futuras da planilha.

| Coluna | Tipo | Obrigatório | Descrição |
|--------|------|-------------|-----------|
| `user_id` | INTEGER FK | Sim | — |
| `plan_id` | INTEGER FK | Não | Planilha relacionada |
| `training_date` | TEXT | Sim | Data do treino |
| `effort_rating` | INTEGER | Não | 1-10 |
| `pain_level` | INTEGER | Não | 0-10 |
| `sleep_quality` | INTEGER | Não | 1-5 |
| `general_feeling` | TEXT | Não | `great` \| `good` \| `ok` \| `bad` \| `very_bad` |
| `notes` | TEXT | Não | Notas livres |
| `ai_analysis` | TEXT | Não | Análise gerada pelo GoJohnny |
| `load_recommendation` | TEXT | Não | `maintain` \| `reduce` \| `increase` |

---

### `conversations`
Sessões de chat com o GoJohnny.

| Coluna | Tipo | Obrigatório | Descrição |
|--------|------|-------------|-----------|
| `user_id` | INTEGER FK | Sim | — |
| `title` | TEXT | Não | Gerado automaticamente |

---

### `messages`
Histórico de mensagens. Alimenta o contexto enviado à Claude API.

| Coluna | Tipo | Obrigatório | Descrição |
|--------|------|-------------|-----------|
| `conversation_id` | INTEGER FK | Sim | — |
| `role` | TEXT | Sim | `user` \| `assistant` \| `system` |
| `content` | TEXT | Sim | Conteúdo da mensagem |
| `tokens_used` | INTEGER | Não | Tokens consumidos (controle de custo) |
| `model_used` | TEXT | Não | Modelo Claude usado |

---

## Estratégia de evolução do schema

1. Toda mudança de schema deve ser uma migration Alembic numerada
2. Nunca alterar colunas existentes diretamente — adicionar novas colunas nullable
3. `extra_context` em `runner_profiles` absorve campos temporários durante exploração
4. `context_snapshot` em `training_plans` preserva rastreabilidade mesmo após updates no perfil
5. Tabelas futuras previstas: `race_registrations`, `strava_integrations`, `user_preferences`
