# Estratégia de Deploy — GoJohnny MVP

**Data:** 2026-04-15  
**Status:** Atualizado com Supabase Auth, OpenAI, e Vercel

---

## Visão geral da arquitetura de deploy

```
┌─────────────────────┐
│  Vercel             │
│  Frontend (Next.js) │
└──────────┬──────────┘
           │ HTTPS
           ▼
┌─────────────────────┐      ┌──────────────────┐
│  Railway/Render     │◄────►│  Supabase        │
│  Backend (FastAPI)  │      │  Auth + Database │
└─────────────────────┘      └──────────────────┘
```

---

## Ambiente de desenvolvimento local

### 1.1 Preparar estrutura

```bash
cd C:\Projetos\gojohnny

# Criar virtualenv
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # Linux/Mac

# Instalar dependências backend
pip install -r backend/requirements.txt

# Instalar dependências frontend
cd frontend
npm install
cd ..
```

### 1.2 Configurar variáveis de ambiente

```bash
# Copiar template
cp .env.example .env
cp frontend/.env.example frontend/.env.local
```

Editar `.env` com valores locais:
```env
APP_ENV=development
DATABASE_URL=sqlite:///./gojohnny.db

# Supabase Auth (obter em: https://app.supabase.com → Settings > API)
SUPABASE_JWT_SECRET=eyJhbGc...
SUPABASE_URL=https://xxxxxxxx.supabase.co

# OpenAI
OPENAI_API_KEY=sk-proj-...
OPENAI_MODEL_CHAT=gpt-4o-mini
OPENAI_MODEL_COACH=gpt-4o

ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000
LOG_LEVEL=DEBUG
```

Editar `frontend/.env.local`:
```env
NEXT_PUBLIC_SUPABASE_URL=https://xxxxxxxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGc...
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

### 1.3 Rodar localmente

**Terminal 1 — Backend:**
```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

Acesse: http://localhost:8000/docs (Swagger)

**Terminal 2 — Frontend:**
```bash
cd frontend
npm run dev
```

Acesse: http://localhost:3000

---

## Produção — Railway (Backend) + Vercel (Frontend)

### Backend: Railway

#### Por que Railway?

- Suporte nativo a Python (Nixpacks detecta automaticamente)
- PostgreSQL gerenciado no mesmo projeto
- Deploy por git push automático
- Free tier adequado para MVP
- Variáveis injetadas via UI segura

#### Passos para deploy

**1. Criar conta e projeto**
- Acesse https://railway.app
- Crie novo projeto
- Conecte repositório GitHub `gojohnny`

**2. Configurar variáveis de ambiente**

Na UI Railway → Settings → Variables, adicionar:

```env
APP_ENV=production
APP_NAME=GoJohnny
APP_VERSION=0.1.0

# Supabase Auth
SUPABASE_JWT_SECRET=<copiar de Supabase Settings > API > JWT Secret>
SUPABASE_URL=<copiar de Supabase Settings > API > Project URL>

# OpenAI
OPENAI_API_KEY=<sua chave>
OPENAI_MODEL_CHAT=gpt-4o-mini
OPENAI_MODEL_COACH=gpt-4o
OPENAI_MAX_TOKENS=2048

# CORS
ALLOWED_ORIGINS=https://[seu-frontend].vercel.app

# Logging
LOG_LEVEL=INFO
```

**3. Adicionar banco PostgreSQL (opcional)**

Se quiser PostgreSQL em Railway:
- [ ] Clique "New" → "Database" → "PostgreSQL"
- [ ] Railway injeta `DATABASE_URL` automaticamente
- [ ] Executar migrations: `alembic upgrade head`

Se usar SQLite:
- `DATABASE_URL=sqlite:///./gojohnny.db` (local ao container — efêmero!)
- Não recomendado para produção (dados são perdidos em restart)

**4. Configurar start command**

Railway detecta `backend/` como raiz Python automaticamente.
Se não detectar, adicione em Settings → Build:

```
Builder: Nixpacks
Start Command: cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

**5. Deploy**

- Fazer push para `main`
- Railway detecta e deploy automaticamente
- Aguardar ~2–3 min

**6. Validar**

```bash
# Health check (sem auth necessário)
curl https://[seu-railway-url].railway.app/health

# Swagger (dev apenas)
https://[seu-railway-url].railway.app/docs
```

### Frontend: Vercel

#### Por que Vercel?

- Otimizado para Next.js (deployment automático)
- Edge network global (CDN)
- Integração com GitHub (deploy automático em push)
- Free tier adequado para MVP

#### Passos para deploy

**1. Criar projeto**
- Acesse https://vercel.com
- Clicar "Import Project"
- Conectar repositório `gojohnny`
- Preencher:
  - **Project Name:** `gojohnny` (ou similar)
  - **Framework:** Next.js (detecção automática)
  - **Root Directory:** `frontend`

**2. Configurar variáveis**

Na UI Vercel → Settings → Environment Variables:

```env
NEXT_PUBLIC_SUPABASE_URL=https://[seu-projeto].supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGc...
NEXT_PUBLIC_API_BASE_URL=https://[seu-backend].railway.app
```

**3. Deploy**

- Clicar "Deploy"
- Vercel detecta `frontend/` automaticamente
- Aguardar ~2–3 min
- URL gerada automática (ex: `gojohnny.vercel.app`)

**4. Validar**

```bash
# Acessar frontend
https://gojohnny.vercel.app

# Verificar que carrega sem erros (F12 → Console)
# Testar login com email de teste
```

---

## Variáveis obrigatórias por ambiente

| Variável | Dev | Prod | Fonte |
|----------|-----|------|-------|
| `DATABASE_URL` | SQLite | PostgreSQL | Railway ou manual |
| `SUPABASE_JWT_SECRET` | Sim | **Sim (crítico)** | Supabase Settings > API |
| `SUPABASE_URL` | Sim | Sim | Supabase Settings > API |
| `OPENAI_API_KEY` | Sim | Sim | OpenAI Platform |
| `APP_ENV` | development | production | Manual |
| `ALLOWED_ORIGINS` | localhost:3000 | https://[vercel-url] | Manual |
| `NEXT_PUBLIC_SUPABASE_URL` | Sim | Sim | Vercel Env Vars |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Sim | Sim | Vercel Env Vars |
| `NEXT_PUBLIC_API_BASE_URL` | localhost:8000 | https://[railway-url] | Vercel Env Vars |

---

## Custo estimado do MVP

| Serviço | Plano | Custo mensal |
|---------|-------|-------------|
| Railway (backend + Postgres) | Free/Hobby | ~$0–5 USD |
| Vercel (frontend) | Free | $0 USD |
| Supabase (auth + db) | Free/Startup | ~$0–25 USD |
| OpenAI API | Pay as you go | ~$5–50 USD (depende do uso) |
| **Total estimado** | | **~$5–80 USD/mês** |

**Otimizações de custo:**
- Usar `gpt-4o-mini` no chat (mais barato que `gpt-4o`)
- Limitar tokens por requisição (`openai_max_tokens=2048`)
- Implementar rate limiting por usuário
- Monitorar custo com Murilo (FinOps) semana 2

### Referência de custo OpenAI:
- `gpt-4o-mini`: $0.15/M tokens input, $0.60/M tokens output
- `gpt-4o`: $5/M tokens input, $15/M tokens output

---

## Monitoramento e alertas

### Recomendado

- [ ] **Railway:** Monitorar CPU, memória, erros
- [ ] **Vercel:** Monitorar latência, erros (automático)
- [ ] **Sentry:** Error tracking (opcional mas recomendado)
- [ ] **Uptime Robot:** Alertar se `/health` falhar

### Logs

- **Backend:** Railway console ou `railway logs` (CLI)
- **Frontend:** Vercel Deployment Analytics
- **Banco:** Supabase SQL Editor → Logs (se disponível)

---

## Troubleshooting de deployment

| Problema | Causa | Solução |
|----------|-------|---------|
| 500 - SUPABASE_JWT_SECRET incorreto | Variável não configurada ou com typo | Verificar em Railway/Vercel Settings |
| 401 - Token JWT expirado | Token expira em 60 min | Frontend deve fazer refresh automático |
| CORS error no frontend | `ALLOWED_ORIGINS` não inclui URL do frontend | Adicionar https://[vercel-url] |
| PostgreSQL connection refused | Banco não pronto ou URL incorreta | Testar com `psql` antes de deploy |
| Vercel 404 no /api/ | Função serverless não encontrada | Verificar se está em `api/` |
| OpenAI rate limit atingido | Muitos requests em pouco tempo | Implementar rate limiting ou aumentar limite na OpenAI |

---

## CI/CD futuro

Recomendações (não implementado no MVP):

- **GitHub Actions:** Rodar testes antes de merge para `main`
- **Staging:** Deploy automático em branch `staging` para testing
- **Approval gate:** Review obrigatório antes de deploy em produção

---

## Referências e documentação

- **Checklist de publicação:** `docs/checklist-publicacao.md`
- **Variáveis de ambiente:** `docs/variaveis-de-ambiente.md`
- **ADR-001 (Supabase Auth):** `docs/adr/ADR-001-infraestrutura-supabase.md`
- **Railway Docs:** https://docs.railway.app
- **Vercel Docs:** https://vercel.com/docs
- **Supabase Docs:** https://supabase.com/docs
