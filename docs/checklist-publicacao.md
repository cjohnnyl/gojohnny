# Checklist de Publicação — GoJohnny

**Data:** 2026-04-15  
**Status:** Pronto para MVP

---

## O que você vai fazer neste checklist

Transformar o GoJohnny de código local em um serviço acessível:
1. Criar e configurar Supabase (auth + banco de dados)
2. Deployar backend em Railway/Render
3. Deployar frontend em Vercel
4. Validar funcionamento completo end-to-end
5. Ir live

**Tempo estimado:** 45–60 min

---

## Etapa 1 — Supabase (Auth + Banco de Dados)

### 1.1 Criar projeto Supabase

- [ ] Acessar https://supabase.com
- [ ] Fazer login / criar conta
- [ ] Clicar em "New Project"
- [ ] Preencher:
  - **Name:** `gojohnny` (ou semelhante)
  - **Database Password:** Gerar senha forte (`openssl rand -base64 32`)
  - **Region:** Mais próxima de você (ex: `sa-east-1` para Brasil)
- [ ] Clicar "Create new project" — aguardar 2–3 min

### 1.2 Habilitar Supabase Auth

- [ ] No projeto, ir para **Authentication** (lado esquerdo)
- [ ] Clicar em "Providers"
- [ ] Clicar em **Email** → habilitar
  - Confirmar que "Email Confirmation" está ativo (recomendado, mas pode desabilitar em dev)
  - Confirmar "Double Confirm Change" desabilitado
- [ ] Voltar à aba **Settings** (em Authentication)
- [ ] Copiar e guardar:
  - **JWT Secret** → `SUPABASE_JWT_SECRET`
  - **Project URL** → `SUPABASE_URL`

### 1.3 Obter credenciais Supabase

- [ ] Ir para **Settings** > **API** (no menu lateral)
- [ ] Copiar:
  - **Project URL** → `NEXT_PUBLIC_SUPABASE_URL` e `SUPABASE_URL`
  - **anon [public]** → `NEXT_PUBLIC_SUPABASE_ANON_KEY`
  - **JWT Secret** → `SUPABASE_JWT_SECRET` (já guardou acima)
  - **service_role [secret]** → guardar para usar após (não compartilhar)
- [ ] Guardar estas variáveis em local seguro (1Password, .env local, etc.)

### 1.4 Configurar Redirect URLs (CORS do Supabase Auth)

- [ ] Em **Settings** > **General** (ainda em Authentication)
- [ ] Descer até "Redirect URLs"
- [ ] Adicionar:
  - `http://localhost:3000/auth/callback` (dev)
  - `https://[seu-frontend-vercel].vercel.app/auth/callback` (produção — adicionar depois)
- [ ] Salvar

### 1.5 Criar schema de banco de dados

- [ ] Ir para **SQL Editor** (lado esquerdo)
- [ ] Clicar em "New Query"
- [ ] Copiar e executar o SQL abaixo:

```sql
-- runner_profiles
CREATE TABLE IF NOT EXISTS runner_profiles (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID NOT NULL UNIQUE,
    name TEXT NOT NULL,
    level TEXT NOT NULL,
    weekly_volume_km REAL,
    available_days_per_week INTEGER,
    preferred_days TEXT,
    comfortable_pace TEXT,
    main_goal TEXT,
    target_race_name TEXT,
    target_race_distance_km REAL,
    target_race_date DATE,
    injury_history TEXT,
    physical_limitations TEXT,
    location TEXT,
    extra_context TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- training_plans
CREATE TABLE IF NOT EXISTS training_plans (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID NOT NULL,
    week_start DATE NOT NULL,
    week_end DATE NOT NULL,
    plan_data JSONB,
    context_snapshot JSONB,
    status TEXT DEFAULT 'active',
    coach_notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (user_id) REFERENCES auth.users(id) ON DELETE CASCADE
);

-- training_feedbacks
CREATE TABLE IF NOT EXISTS training_feedbacks (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID NOT NULL,
    plan_id BIGINT,
    training_date DATE NOT NULL,
    effort_rating INTEGER,
    pain_level INTEGER,
    sleep_quality INTEGER,
    general_feeling TEXT,
    notes TEXT,
    ai_analysis TEXT,
    load_recommendation TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (user_id) REFERENCES auth.users(id) ON DELETE CASCADE,
    FOREIGN KEY (plan_id) REFERENCES training_plans(id) ON DELETE SET NULL
);

-- conversations
CREATE TABLE IF NOT EXISTS conversations (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID NOT NULL,
    title TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (user_id) REFERENCES auth.users(id) ON DELETE CASCADE
);

-- messages
CREATE TABLE IF NOT EXISTS messages (
    id BIGSERIAL PRIMARY KEY,
    conversation_id BIGINT NOT NULL,
    role TEXT NOT NULL,
    content TEXT NOT NULL,
    tokens_used INTEGER,
    model_used TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
);

-- runner_memory
CREATE TABLE IF NOT EXISTS runner_memory (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID NOT NULL UNIQUE,
    active_plan_id BIGINT,
    plan_week_current INTEGER,
    plan_week_total INTEGER,
    plan_started_at DATE,
    week_progress JSONB,
    recent_feedbacks JSONB,
    physical_alerts JSONB,
    load_adjustments JSONB,
    chat_observations JSONB,
    last_coaching_style TEXT,
    last_session_summary TEXT,
    last_session_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (user_id) REFERENCES auth.users(id) ON DELETE CASCADE
);

-- Índices
CREATE INDEX idx_training_plans_user_id ON training_plans(user_id);
CREATE INDEX idx_training_feedbacks_user_id ON training_feedbacks(user_id);
CREATE INDEX idx_conversations_user_id ON conversations(user_id);
CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX idx_runner_memory_user_id ON runner_memory(user_id);

-- RLS (Row-Level Security) — opcional mas recomendado
ALTER TABLE runner_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE training_plans ENABLE ROW LEVEL SECURITY;
ALTER TABLE training_feedbacks ENABLE ROW LEVEL SECURITY;
ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE runner_memory ENABLE ROW LEVEL SECURITY;

-- Políticas RLS
CREATE POLICY "Users can view own runner_profile"
    ON runner_profiles FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can update own runner_profile"
    ON runner_profiles FOR UPDATE
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own runner_profile"
    ON runner_profiles FOR INSERT
    WITH CHECK (auth.uid() = user_id);

-- (Aplicar políticas semelhantes para outras tabelas)
```

- [ ] Executar (Ctrl+Enter)
- [ ] Verificar que não há erros
- [ ] Ir para **Table Editor** e confirmar que tabelas foram criadas

---

## Etapa 2 — Backend (FastAPI em Railway/Render)

### 2.1 Preparar repositório

- [ ] Clonar ou atualizar repositório local:
  ```bash
  cd C:\Projetos\gojohnny
  git pull origin main
  ```

- [ ] Verificar que `.env` está no `.gitignore`:
  ```bash
  cat .gitignore | grep -E "\.env|secrets"
  ```

- [ ] Se não estiver, adicionar:
  ```
  .env
  .env.*.local
  *.db
  ```

### 2.2 Criar projeto em Railway (ou Render)

**Opção A: Railway**

- [ ] Acessar https://railway.app
- [ ] Fazer login / criar conta
- [ ] Clicar "New Project"
- [ ] Clicar "Deploy from GitHub"
- [ ] Conectar conta GitHub
- [ ] Selecionar repositório `gojohnny`
- [ ] Railway detecta automaticamente que é Python (Nixpacks)

**Opção B: Render**

- [ ] Acessar https://render.com
- [ ] Fazer login / criar conta
- [ ] Clicar "New +" > "Web Service"
- [ ] Conectar repositório GitHub `gojohnny`
- [ ] Preencher:
  - **Name:** `gojohnny-api`
  - **Environment:** `Python 3.11`
  - **Build Command:** `pip install -r backend/requirements.txt && cd backend && alembic upgrade head`
  - **Start Command:** `cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### 2.3 Configurar variáveis de ambiente (Railway)

- [ ] No dashboard Railway, ir para **Variables**
- [ ] Adicionar:

```env
APP_ENV=production
APP_NAME=GoJohnny
APP_VERSION=0.1.0

DATABASE_URL=[gerado automaticamente pelo Railway se add PostgreSQL, ou manual]
SUPABASE_JWT_SECRET=[copiar de Supabase Settings > API > JWT Secret]
SUPABASE_URL=[copiar de Supabase Settings > API > Project URL]

OPENAI_API_KEY=[copiar de OpenAI Platform]
OPENAI_MODEL_CHAT=gpt-4o-mini
OPENAI_MODEL_COACH=gpt-4o
OPENAI_MAX_TOKENS=2048

ALLOWED_ORIGINS=https://[seu-projeto].vercel.app,http://localhost:3000
LOG_LEVEL=INFO
```

- [ ] Clicar "Deploy" (se não iniciou automaticamente)
- [ ] Aguardar ~2–3 min

### 2.4 Validar backend

- [ ] Acessar URL do Railway (ex: `https://gojohnny.railway.app`)
  ```bash
  curl https://gojohnny.railway.app/health
  ```
- [ ] Verificar resposta: `{"status": "ok"}`
- [ ] Acessar Swagger (dev apenas):
  ```
  https://gojohnny.railway.app/docs
  ```

---

## Etapa 3 — Frontend (Next.js em Vercel)

### 3.1 Preparar código frontend

- [ ] No repositório, verificar que `frontend/` existe e tem `package.json`
- [ ] Verificar `.env.example` com variáveis necessárias:
  ```env
  NEXT_PUBLIC_SUPABASE_URL=
  NEXT_PUBLIC_SUPABASE_ANON_KEY=
  NEXT_PUBLIC_API_BASE_URL=
  ```
- [ ] Commitar e fazer push para `main`:
  ```bash
  git add .
  git commit -m "feat: frontend ready for Vercel deploy"
  git push origin main
  ```

### 3.2 Criar projeto em Vercel

- [ ] Acessar https://vercel.com
- [ ] Fazer login / criar conta (pode usar GitHub)
- [ ] Clicar "Import Project"
- [ ] Selecionar repositório `gojohnny`
- [ ] Preencher:
  - **Project Name:** `gojohnny-frontend` (ou semelhante)
  - **Root Directory:** `frontend`
  - **Framework Preset:** Next.js (detecta automaticamente)
- [ ] Clicar "Continue"

### 3.3 Configurar variáveis (Vercel)

- [ ] Na página de configuração, ir para **Environment Variables**
- [ ] Adicionar:

```env
NEXT_PUBLIC_SUPABASE_URL=[copiar de Supabase Settings > API > Project URL]
NEXT_PUBLIC_SUPABASE_ANON_KEY=[copiar de Supabase Settings > API > anon key]
NEXT_PUBLIC_API_BASE_URL=https://[seu-backend-railway].railway.app
```

- [ ] Clicar "Deploy"
- [ ] Aguardar ~2–3 min

### 3.4 Validar frontend

- [ ] Acessar URL do Vercel (ex: `https://gojohnny-frontend.vercel.app`)
- [ ] Verificar que página carrega sem erros de console
- [ ] Ir para **Settings** > **Deployments** e confirmar URL

### 3.5 Adicionar Redirect URL ao Supabase

- [ ] Voltar ao Supabase Console
- [ ] Ir para **Authentication** > **Settings**
- [ ] Adicionar a Redirect URL:
  ```
  https://[seu-frontend].vercel.app/auth/callback
  ```
- [ ] Salvar

---

## Etapa 4 — Testes End-to-End

### 4.1 Teste de autenticação

- [ ] Acessar frontend Vercel
- [ ] Clicar em "Sign Up"
- [ ] Preencher email e senha
- [ ] Verificar email de confirmação (ou direto ao dashboard se confirmação desabilitada)
- [ ] Fazer login com email + senha
- [ ] Verificar que JWT é armazenado no `localStorage` ou `sessionStorage`

### 4.2 Teste de perfil

- [ ] Após login, ir para "Perfil" ou equivalente
- [ ] Preencher dados básicos (nível, dias disponíveis, objetivo)
- [ ] Salvar
- [ ] Verificar que dados retornam na próxima página de refresh

### 4.3 Teste de chat

- [ ] Ir para "Chat" ou equivalente
- [ ] Enviar mensagem simples: "Oi, como você funciona?"
- [ ] Verificar que resposta chega em ~2–5 segundos
- [ ] Enviar mensagem sobre treino: "Recomenda um treino hoje?"
- [ ] Verificar que resposta é contextualizada ao perfil

### 4.4 Teste de integração completa

- [ ] Gerar um plano semanal
- [ ] Registrar um feedback de treino
- [ ] Enviar nova mensagem no chat
- [ ] Verificar que contexto dinâmico afeta resposta

---

## Etapa 5 — Go Live

### 5.1 Verificações finais

- [ ] [ ] Backend health check funciona
- [ ] [ ] Frontend carrega sem erros
- [ ] [ ] Login/logout funciona
- [ ] [ ] Chat responde em tempo razoável (<5s)
- [ ] [ ] Banco de dados está acessível (testar com psql ou DBeaver)
- [ ] [ ] Logs estão sendo capturados (Railway logs)
- [ ] [ ] CORS não está bloqueando requisições

### 5.2 Documentação atualizada

- [ ] [ ] README aponta para URLs corretas (Supabase, Vercel, Railway)
- [ ] [ ] Arquivo `.env.example` atualizado com variáveis necessárias
- [ ] [ ] Documentação de deployment está completa
- [ ] [ ] ADRs registram decisões tomadas

### 5.3 Anúncio

- [ ] [ ] Compartilhar URL do GoJohnny com usuários finais
- [ ] [ ] Instruir novos usuários a fazer signup
- [ ] [ ] Monitorar logs e feedback nos primeiros dias
- [ ] [ ] Estar pronto para hotfixes rápidos se necessário

---

## Troubleshooting Rápido

| Problema | Solução |
|----------|---------|
| **"SUPABASE_JWT_SECRET is not set"** | Copiar JWT Secret correto de Settings > API > JWT Secret e adicionar ao Railway/Render |
| **"CORS error"** | Adicionar URL do frontend a `ALLOWED_ORIGINS` no backend |
| **"Auth redirect loop"** | Verificar Redirect URLs em Supabase Auth Settings |
| **"500 error no chat"** | Verificar `OPENAI_API_KEY` e se modelo existe (`gpt-4o-mini` é válido?) |
| **"Database connection refused"** | Verificar `DATABASE_URL` e se PostgreSQL está rodando |
| **"Frontend não carrega"** | Verificar console do browser (F12) para erros de CORS ou variável faltante |

---

## Próximos passos (Pós-MVP)

- [ ] Habilitar Google/Apple login em Supabase Auth
- [ ] Configurar Sentry para error tracking em produção
- [ ] Adicionar testes automatizados (E2E com Playwright)
- [ ] Integrar Strava API para dados de treino
- [ ] Implementar dashboard de progresso
- [ ] Adicionar exportação de plano/chat em PDF

---

## Referências

- **Supabase Docs:** https://supabase.com/docs
- **Railway Docs:** https://docs.railway.app
- **Vercel Docs:** https://vercel.com/docs
- **FastAPI Docs:** https://fastapi.tiangolo.com
- **Next.js Docs:** https://nextjs.org/docs
- **GoJohnny ADR-001:** `/docs/adr/ADR-001-infraestrutura-supabase.md`
- **GoJohnny Variáveis de Ambiente:** `/docs/variaveis-de-ambiente.md`
