# Arquitetura Inicial — GoJohnny MVP

**Versão:** 0.1.0
**Data:** 2026-04-13
**Status:** Aprovado para MVP

---

## Visão Geral

O GoJohnny é uma API conversacional especializada em corrida de rua.
No MVP, opera exclusivamente como backend (API REST), sem frontend dedicado.
A interface de uso é o Swagger UI gerado pelo FastAPI.

---

## Stack

| Camada | Tecnologia | Versão mínima |
|--------|-----------|---------------|
| Backend | Python + FastAPI | 3.11+ / 0.115+ |
| ORM | SQLAlchemy + Alembic | 2.0+ / 1.14+ |
| Banco (dev) | SQLite | 3.x |
| Banco (prod) | PostgreSQL via Railway | 15+ |
| Auth | JWT — python-jose + passlib | — |
| IA | Anthropic Claude API | SDK 0.40+ |
| Logging | Loguru | 0.7+ |
| Hosting | Railway | — |

---

## Estrutura do Projeto

```
C:\Projetos\gojohnny\
├── backend/
│   ├── app/
│   │   ├── core/
│   │   │   ├── config.py        ← Settings via pydantic-settings
│   │   │   └── database.py      ← Engine, Session, Base
│   │   ├── models/
│   │   │   ├── user.py
│   │   │   ├── runner_profile.py
│   │   │   ├── training_plan.py
│   │   │   ├── training_feedback.py
│   │   │   └── conversation.py  ← Conversation + Message
│   │   ├── schemas/             ← Pydantic schemas (request/response)
│   │   ├── services/            ← Lógica de negócio + integração IA
│   │   ├── routes/              ← Endpoints FastAPI
│   │   └── main.py              ← App entry point
│   ├── migrations/
│   │   └── 001_initial_schema.sql
│   └── requirements.txt
├── docs/
│   ├── arquitetura-inicial.md   ← Este arquivo
│   ├── banco-de-dados.md
│   ├── deploy.md
│   └── adr/
├── .env.example
└── README.md
```

---

## Modelagem de Dados

### Tabelas e responsabilidades

| Tabela | Propósito |
|--------|-----------|
| `users` | Identidade e autenticação |
| `runner_profiles` | Contexto do corredor — alimenta todas as recomendações |
| `training_plans` | Planilhas semanais geradas pela IA |
| `training_feedbacks` | Feedback pós-treino para adaptação futura |
| `conversations` | Sessões de chat |
| `messages` | Histórico de mensagens (user + assistant) |

### Campos críticos para gerar a planilha inicial

Para que o GoJohnny gere uma planilha mínima útil, são obrigatórios:
- `runner_profiles.level`
- `runner_profiles.available_days_per_week`
- `runner_profiles.main_goal`

Campos opcionais que melhoram a recomendação:
- `weekly_volume_km`, `comfortable_pace`, `target_race_date`, `injury_history`

---

## Fluxo de Integração com IA

```
usuário → POST /chat/message
  → valida JWT
  → carrega perfil do corredor (runner_profiles)
  → carrega histórico recente (últimas N mensagens da conversation)
  → monta system prompt com contexto do corredor
  → chama Anthropic Claude API
  → persiste resposta em messages
  → retorna resposta ao usuário
```

### Modelos Claude usados

| Caso de uso | Modelo | Motivo |
|-------------|--------|--------|
| Chat geral | `claude-haiku-4-5-20251001` | Velocidade e custo |
| Geração de planilha semanal | `claude-sonnet-4-6` | Qualidade e raciocínio |
| Análise de feedback | `claude-sonnet-4-6` | Precisão na leitura de sinais |

### Guardrails (implementação no system prompt)

- Não diagnosticar lesões
- Não prescrever tratamento médico
- Redirecionar para profissional em caso de sinais de risco
- Manter foco exclusivo em corrida de rua e temas correlatos
- Usar linguagem inclusiva, sem assumir perfil

---

## Autenticação

- Fluxo: email + senha → JWT access token + refresh token
- Access token: 60 min
- Refresh token: 30 dias
- Hash de senha: bcrypt (via passlib)
- Sem OAuth no MVP (pode ser adicionado depois)

---

## Observabilidade

| Recurso | Solução | Status |
|---------|---------|--------|
| Logs estruturados | Loguru | MVP |
| Rastreio de erros | Sentry (opcional) | Configurado via env |
| Tokens de IA por request | Salvo em `messages.tokens_used` | MVP |
| Monitoramento de latência | — | Pós-MVP |

---

## Evolução do Schema

O schema foi desenhado para evoluir sem quebrar o MVP:

1. `runner_profiles.extra_context` absorve campos futuros não estruturados
2. `training_plans.context_snapshot` permite rastrear o estado do perfil no momento da geração
3. `messages.model_used` e `tokens_used` viabilizam controle de custo por usuário
4. Tabelas de integração (Strava, apps externos) serão adicionadas em migrations futuras

---

## Decisões de Arquitetura

| Decisão | Escolha | Alternativa considerada | Motivo |
|---------|---------|------------------------|--------|
| Banco dev | SQLite | Postgres local | Zero setup, funciona imediatamente |
| Banco prod | Postgres via Railway | Supabase | Railway já hospeda o backend, custo menor |
| Auth | JWT próprio | Auth0, Supabase Auth | Sem dependência externa no MVP |
| IA | Claude API | OpenAI | Ecossistema nativo do projeto |
| Hosting | Railway | Vercel, Render | Suporte nativo Python + Postgres gerenciado |
| Interface | API-first | Frontend web | Reduz escopo do MVP, valida lógica primeiro |
