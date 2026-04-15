# ADR-001 — Migração para Supabase Auth e PostgreSQL

**Data:** 2026-04-15  
**Status:** Aceito  
**Autores:** mateus-architect-techlead, laura-orquestradora

---

## Contexto

O GoJohnny MVP foi inicialmente desenhado com:
- Backend FastAPI com JWT próprio (`python-jose` + `passlib`)
- SQLite no desenvolvimento
- PostgreSQL via Railway em produção
- Autenticação por email + hash bcrypt

Após as primeiras sessões de feedback, identificou-se que manter infraestrutura de autenticação própria adiciona overhead operacional (secret rotation, rate limiting, session management) sem agregar valor ao diferencial do produto (coaching conversacional especializado).

Além disso, um usuário pediu explicitamente a integração com ferramentas externas (potencialmente Strava, dispositivos wearables), o que exige federação de identidade — tarefa complexa em JWT caseiro.

---

## Opções Avaliadas

### A. Manter JWT próprio + Railway
**Prós:**
- Zero dependências de terceiros para auth
- Controle total sobre tokens e sessões

**Contras:**
- Mais código a manter
- Sem federação de identidade
- Sem autenticação social pronta
- Rate limiting manual

**Custo:** ~$5/mês (Railway)

---

### B. Supabase Auth + Supabase PostgreSQL (completo)
**Prós:**
- Auth integrada (email, OAuth, SAML, magic links)
- PostgreSQL gerenciado automaticamente
- RLS (Row-Level Security) nativo
- JWT HS256 emitido pelo Supabase
- Federação de identidade pronta para futuras integrações

**Contras:**
- Dependência de Supabase como provedor
- Custo escala com conectivos (possível problema em longo prazo)

**Custo:** ~$25/mês (Postgres 2GB) + $0.25/1M auth requests

---

### C. Auth0 + PostgreSQL (Railway)
**Prós:**
- Padrão de indústria
- Suporta OAuth 2.0 completo

**Contras:**
- Custo mais alto (~$150–300/mês em produção)
- Overhead de integração
- Não agrega valor proporcional ao estágio do MVP

**Custo:** ~$15/mês (free tier) → $150/mês (produção)

---

### D. Migração gradual: FastAPI + Supabase Auth, banco próprio
**Prós:**
- Reduz escopo: apenas auth migra
- Backend permanece com lógica conhecida
- Pode migrar banco depois

**Contras:**
- Dois fluxos diferentes em dev vs prod
- Desobriga nada (ainda precisa manter Database URL)

---

## Decisão

**Opção D: Migração gradual com Supabase Auth**

- Backend FastAPI mantém toda lógica de negócio (sem mudanças)
- JWT agora é emitido pelo Supabase (HS256)
- FastAPI valida JWT usando `SUPABASE_JWT_SECRET` (Settings > API > JWT Secret)
- `user_id` muda de `int` para `UUID` (Supabase usa UUID para auth users)
- Banco pode inicialmente permanecer em SQLite dev / Railway prod — migração para Supabase Postgres é opcional e pode vir depois
- Nova tabela `runner_memory` armazena contexto dinâmico (decisão paralela — ADR-002)

---

## Consequências

### Removido
- Rota `/auth/register` (usuários criam conta via Supabase UI ou cliente)
- Rota `/auth/login` (JWT vem do Supabase — cliente chama Supabase Auth diretamente)
- Arquivo `app/routes/auth.py` (lógica de auth saiu do FastAPI)
- Tabela `users` (usuarios agora gerenciados por Supabase Auth)
- Campo `password_hash` (senhas nunca saem do Supabase)
- Models `User` e `UserSchema`

### Adicionado
- Middleware FastAPI para validar JWT Supabase
- Endpoint `GET /health` — health check do backend (para Vercel validar)
- Header `Authorization: Bearer <jwt_token>` obrigatório em todos endpoints autenticados
- Variável de ambiente `SUPABASE_JWT_SECRET`

### Modificado
- Campo `user_id` de `INTEGER PK` para `UUID` em:
  - `runner_profiles`
  - `conversations`
  - `training_plans`
  - `training_feedbacks`
  - `runner_memory` (nova tabela)
- Schemas Pydantic que usam `user_id`: agora esperam UUID, não int
- Deps (`get_current_user`) extrai UUID do JWT payload

### Variáveis de ambiente necessárias

**Backend (Railway/Render):**
```env
# App
APP_ENV=production
APP_NAME=GoJohnny
APP_VERSION=0.1.0

# Database
DATABASE_URL=postgresql://user:pass@host:5432/gojohnny

# Supabase Auth (JWT validation)
SUPABASE_JWT_SECRET=<JWT Secret from Settings > API > JWT Secret>
SUPABASE_URL=https://xxxxxxxx.supabase.co

# OpenAI
OPENAI_API_KEY=sk-...
OPENAI_MODEL_CHAT=gpt-4o-mini
OPENAI_MODEL_COACH=gpt-4o
OPENAI_MAX_TOKENS=2048

# Networking
ALLOWED_ORIGINS=https://[seu-frontend].vercel.app,http://localhost:3000
LOG_LEVEL=INFO
```

**Frontend (Vercel):**
```env
NEXT_PUBLIC_SUPABASE_URL=https://xxxxxxxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
NEXT_PUBLIC_API_BASE_URL=https://[seu-backend].railway.app
```

---

## Justificativa

1. **Reduz escopo do MVP:** Auth é infraestrutura, não diferencial
2. **Federação de identidade pronta:** Abre porta para Strava, Apple Health, Garmin
3. **Segurança delegada:** Supabase mantém senhas, não o GoJohnny
4. **Custo proporcional ao estágio:** $25–50/mês vs $150+ com Auth0
5. **Gradual:** Banco pode migrar depois — não bloqueia MVP

---

## Alternativas descartadas e por quê

- **Auth0:** Custo desproporcional para MVP + overhead de integração
- **Firebase/Google Cloud:** Vendor lock-in maior, não suporta Python nativo no backend
- **Manter JWT próprio:** Impossível sem redesenhar autenticação social futura

---

## Próximas decisões relacionadas

- **ADR-002:** Estratégia de memória útil do corredor (contexto dinâmico no prompt)
- **Futuro:** Migração do banco SQLite/Railway para Supabase PostgreSQL (não bloqueia MVP)
- **Futuro:** Integração Strava/Apple Health com OAuth delegado

---

## Validação

- [ ] Supabase Auth configurado (email + password)
- [ ] JWT Secret copiado para `SUPABASE_JWT_SECRET`
- [ ] Middleware FastAPI valida JWT com sucesso
- [ ] Teste: login via Supabase → JWT → POST /chat/message funciona
- [ ] CORS permite requisições do frontend Vercel
- [ ] Database connection string aponta para banco correto (dev: SQLite / prod: Railway PostgreSQL)
