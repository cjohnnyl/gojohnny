# Variáveis de Ambiente — GoJohnny

**Data:** 2026-04-15  
**Status:** Atualizado com Supabase Auth e OpenAI

---

## Visão Geral

O GoJohnny opera com 3 ambientes:
1. **Desenvolvimento local** (SQLite, auth manual, OpenAI API)
2. **Staging** (banco de teste, API de teste)
3. **Produção** (PostgreSQL em Railway/Render, Supabase Auth, OpenAI produção)

---

## Backend (FastAPI)

### Desenvolvimento Local

```env
# App
APP_ENV=development
APP_NAME=GoJohnny
APP_VERSION=0.1.0
APP_DEBUG=true

# Database — SQLite padrão (cria gojohnny.db no diretório raiz)
DATABASE_URL=sqlite:///./gojohnny.db

# Supabase Auth (JWT validation)
# Obter em: https://app.supabase.com → Settings > API > JWT Secret
SUPABASE_JWT_SECRET=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_URL=https://[seu-projeto].supabase.co

# OpenAI
# Obter em: https://platform.openai.com/account/api-keys
OPENAI_API_KEY=sk-proj-...
OPENAI_MODEL_CHAT=gpt-4o-mini
OPENAI_MODEL_COACH=gpt-4o
OPENAI_MAX_TOKENS=2048

# CORS
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000

# Logging
LOG_LEVEL=DEBUG

# Sentry (opcional)
SENTRY_DSN=
```

### Staging

```env
APP_ENV=staging
APP_NAME=GoJohnny
APP_VERSION=0.1.0
APP_DEBUG=false

# Database — PostgreSQL em staging
DATABASE_URL=postgresql://user:pass@staging-db.railway.app:5432/gojohnny_staging

# Supabase Auth
SUPABASE_JWT_SECRET=<JWT secret da instância staging>
SUPABASE_URL=https://[seu-projeto-staging].supabase.co

# OpenAI — pode usar modelo menor em staging para economizar
OPENAI_API_KEY=sk-proj-...
OPENAI_MODEL_CHAT=gpt-4o-mini
OPENAI_MODEL_COACH=gpt-4o-mini
OPENAI_MAX_TOKENS=2048

# CORS
ALLOWED_ORIGINS=https://[seu-projeto-staging].vercel.app

# Logging
LOG_LEVEL=INFO

# Sentry (opcional)
SENTRY_DSN=https://...@sentry.io/...
```

### Produção

```env
APP_ENV=production
APP_NAME=GoJohnny
APP_VERSION=0.1.0
APP_DEBUG=false

# Database — PostgreSQL em Railway/Render
# Railway injeta automaticamente: DATABASE_URL
# Se usar Render: DATABASE_URL=postgresql://user:pass@prod-db.render.com:5432/gojohnny
DATABASE_URL=postgresql://user:pass@host:5432/gojohnny

# Supabase Auth — CRÍTICO: usar secret correto da instância produção
SUPABASE_JWT_SECRET=<JWT Secret da instância produção — NUNCA usar staging aqui>
SUPABASE_URL=https://[seu-projeto].supabase.co

# OpenAI — use modelos recomendados
OPENAI_API_KEY=sk-proj-...
OPENAI_MODEL_CHAT=gpt-4o-mini
OPENAI_MODEL_COACH=gpt-4o
OPENAI_MAX_TOKENS=2048

# CORS — apenas URL de produção do frontend
ALLOWED_ORIGINS=https://gojohnny.vercel.app

# Logging
LOG_LEVEL=INFO

# Sentry — RECOMENDADO para produção
SENTRY_DSN=https://[seu-token]@sentry.io/[seu-project-id]
```

---

## Frontend (Next.js + Vercel)

### Desenvolvimento Local

```env
# Supabase
# Obter em: https://app.supabase.com → Settings > API > Project URL e anon key
NEXT_PUBLIC_SUPABASE_URL=https://[seu-projeto].supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# API
# Aponta para backend local
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

### Produção (Vercel)

```env
# Supabase — mesma instância que o backend usa
NEXT_PUBLIC_SUPABASE_URL=https://[seu-projeto].supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# API — aponta para backend em produção (Railway/Render)
NEXT_PUBLIC_API_BASE_URL=https://gojohnny-api.railway.app
```

---

## Referência Rápida

### Onde obter cada variável

| Variável | Fonte | Ambiente | Exemplo |
|----------|-------|----------|---------|
| `SUPABASE_JWT_SECRET` | Supabase Console → Settings > API > JWT Secret | Todos | `eyJhbGc...` |
| `SUPABASE_URL` | Supabase Console → Settings > API > Project URL | Todos | `https://abc.supabase.co` |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Supabase Console → Settings > API > Anon Key | Todos | `eyJhbGc...` |
| `OPENAI_API_KEY` | OpenAI Platform → API Keys | Todos | `sk-proj-...` |
| `DATABASE_URL` | Railway Console ou `.env.local` | Dev/Prod | `postgresql://...` ou `sqlite:///...` |
| `NEXT_PUBLIC_API_BASE_URL` | Manual (URL do backend) | Dev/Prod | `http://localhost:8000` ou `https://...railway.app` |

---

## Segurança

### ✅ FAZER

- Armazenar segredos em `1Password`, `Vault` ou `AWS Secrets Manager`
- Usar variáveis de ambiente do provedor (Railway/Vercel) para dados sensíveis
- Rotar `SUPABASE_JWT_SECRET` a cada 6 meses
- Usar `.env.local` em dev (nunca commitar)
- Adicionar `.env`, `.env.*.local` ao `.gitignore`

### ❌ NÃO FAZER

- Commitar chaves de API no repositório
- Usar mesma chave em dev e produção
- Compartilhar chaves em Slack/email
- Deixar chaves em comentários de código

---

## Validação

Após configurar variáveis, teste:

**Backend:**
```bash
# Health check
curl -X GET http://localhost:8000/health

# Swagger (dev apenas)
http://localhost:8000/docs
```

**Frontend:**
```bash
# Deve conectar ao Supabase sem erro
# Deve conseguir fazer login
# Chat deve conseguir chamar backend (verificar CORS)
```

---

## Troubleshooting

### 500 - SUPABASE_JWT_SECRET incorreto
- Verificar se copiou o Secret completo em Settings > API > JWT Secret
- Não misturar secret de dev com produção

### 401 - Token JWT inválido
- JWT pode estar expirado (60 min de TTL)
- Refresh token pode estar expirado (30 dias)
- Frontend precisa renovar token automaticamente

### CORS error ao chamar backend
- Verificar `ALLOWED_ORIGINS` no backend (deve incluir URL do frontend)
- Verificar se frontend está enviando header `Authorization: Bearer <token>`

### Banco de dados não conecta
- Dev: verificar se SQLite está no diretório certo (`gojohnny.db` na raiz)
- Prod: testar connection string com `psql` antes de deployar
- Railway: PostgreSQL pode levar 1-2 min para ficar pronto após criação

---

## Próximos passos

- Adicionar variáveis de custo/FinOps (tokens trackados em `messages` e `training_feedbacks`)
- Adicionar variáveis de integração (Strava OAuth — futuro)
- Documentar rotação de secrets em produção
