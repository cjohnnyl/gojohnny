# CLAUDE.md — GoJohnny

## O que é GoJohnny?

GoJohnny é um treinador digital de corrida de rua. Funciona como um chatbot especialista que acompanha corredores com recomendações personalizadas, gera planos de treino semanais adaptados ao perfil do usuário, analisa feedback pós-treino e mantém memória de contexto contínua.

## Stack Técnica

**Backend:**
- Python 3.11+ + FastAPI
- SQLAlchemy 2.x + Alembic (ORM + migrações)
- Supabase Auth (JWKS/RS256)
- OpenAI API (gpt-4o-mini para chat, gpt-4o para planos)
- Railway (hosting)

**Frontend:**
- Next.js 15 + React 19 + TypeScript
- Supabase JS SDK
- Tailwind CSS v4
- Vercel (hosting)

**Banco de Dados:**
- SQLite (desenvolvimento)
- PostgreSQL (produção via Railway)

## Estrutura de Pastas

```
gojohnny/
├── backend/
│   ├── app/
│   │   ├── main.py              # Aplicação FastAPI (entrada)
│   │   ├── core/
│   │   │   ├── config.py        # Configurações via pydantic-settings
│   │   │   └── database.py      # SQLAlchemy engine + sessionmaker
│   │   ├── models/              # Modelos ORM (User, Conversation, RunnerProfile, etc)
│   │   ├── routes/              # Routers FastAPI (chat, profile, plans, feedback, memory)
│   │   ├── schemas/             # Pydantic schemas (request/response)
│   │   └── services/
│   │       ├── ai.py            # Integração com OpenAI
│   │       ├── memory_service.py # Gerenciamento de memória do corredor
│   │       └── deps.py          # Dependências FastAPI (autenticação, etc)
│   ├── migrations_alembic/      # Alembic migrations
│   ├── tests/                   # Testes pytest
│   └── requirements.txt         # Dependências Python
├── frontend/
│   ├── app/
│   │   ├── page.tsx             # Home
│   │   ├── chat/page.tsx        # Chat (conversas)
│   │   ├── onboarding/page.tsx  # Onboarding (criar perfil)
│   │   ├── login/page.tsx       # Login
│   │   ├── plano/page.tsx       # Planos de treino
│   │   ├── layout.tsx           # Root layout
│   │   ├── middleware.ts        # Proteção de rotas
│   │   └── components/          # Componentes React
│   ├── lib/
│   │   ├── api.ts              # Cliente HTTP (fetch com auth)
│   │   ├── supabase.ts         # Cliente Supabase
│   │   └── supabase-server.ts  # Supabase SSR
│   ├── package.json
│   └── tsconfig.json
├── docs/
│   ├── variaveis-de-ambiente.md # Config de variáveis (dev/staging/prod)
│   ├── banco-de-dados.md
│   ├── deploy.md
│   ├── adr/                    # Architecture Decision Records
│   └── api.md                  # Documentação de endpoints
├── .env.example                # Template de variáveis de ambiente
└── README.md                   # Este arquivo
```

## Como Rodar Localmente

### 1. Backend (FastAPI)

```bash
# Setup inicial
python -m venv .venv
.venv\Scripts\activate  # Windows
# ou: source .venv/bin/activate  # Linux/Mac

# Instalar dependências
pip install -r requirements.txt

# Configurar variáveis de ambiente
cp .env.example .env
# Editar .env com:
# - OPENAI_API_KEY (de https://platform.openai.com/account/api-keys)
# - SUPABASE_URL e SUPABASE_ANON_KEY (de https://app.supabase.com)

# Rodar backend
uvicorn backend.app.main:app --reload --port 8000
```

Acesse em dev: `http://localhost:8000/docs` (Swagger)

### 2. Frontend (Next.js)

```bash
cd frontend

npm install

# Variáveis de ambiente (já estão em .env.example na raiz):
# - NEXT_PUBLIC_SUPABASE_URL
# - NEXT_PUBLIC_SUPABASE_ANON_KEY
# - NEXT_PUBLIC_API_URL

npm run dev
```

Acesse em: `http://localhost:3000`

### 3. Banco de Dados

**Desenvolvimento (SQLite):**
- Criado automaticamente no startup em `./gojohnny.db`
- Migrado com Alembic

**Produção (PostgreSQL via Railway):**
- Railway injeta `DATABASE_URL` automaticamente
- Alembic migrations rodadas no deploy

## Como Rodar os Testes

```bash
# Testes backend
pytest backend/tests -v

# Coverage
pytest backend/tests --cov=backend/app
```

## Variáveis de Ambiente

Veja `.env.example` para template completo. Variáveis obrigatórias:

- `OPENAI_API_KEY` - Chave de API do OpenAI
- `SUPABASE_URL` - URL do projeto Supabase
- `SUPABASE_ANON_KEY` - Chave anon do Supabase
- `DATABASE_URL` - String de conexão (SQLite ou PostgreSQL)

Para frontend em produção:
- `NEXT_PUBLIC_SUPABASE_URL`
- `NEXT_PUBLIC_SUPABASE_ANON_KEY`
- `NEXT_PUBLIC_API_URL` - URL do backend em produção

Veja `docs/variaveis-de-ambiente.md` para configuração por ambiente (dev/staging/prod).

## Convenções do Projeto

### Code Style
- Backend: Black (implícito via lint), type hints obrigatórios
- Frontend: ESLint + Next.js defaults, TypeScript strict

### Nomes
- Variáveis/funções: `snake_case` (Python), `camelCase` (TypeScript)
- Arquivos: `snake_case.py`, `PascalCase.tsx` (componentes)
- Routes: lowercase com underscore (`/chat/message`, `/plans/generate`)

### Branching
- `main` - produção
- `develop` - staging (opcional)
- Feature branches: `feat/xyz`, `fix/abc`, `docs/xyz`

### Commit Messages
- Português: "feat: adicionar chat", "fix: corrigir auth"
- Imperativo: "Adicionar" não "Adicionado"

### API
- RESTful com Bearer tokens (Supabase JWT)
- Respostas: JSON com `detail` em erros
- Status codes: 200/201/400/401/404/409/422/500

## Links Importantes

**Documentação do Projeto:**
- [Variáveis de Ambiente](docs/variaveis-de-ambiente.md)
- [Banco de Dados](docs/banco-de-dados.md)
- [Deploy](docs/deploy.md)
- [API Endpoints](docs/api.md)

**Arquitetura (ADRs):**
- [docs/adr/](docs/adr/) - Architecture Decision Records (migrações, auth, IA, etc)

**Referências Externas:**
- [FastAPI docs](https://fastapi.tiangolo.com/)
- [Next.js docs](https://nextjs.org/docs)
- [Supabase docs](https://supabase.com/docs)
- [OpenAI API docs](https://platform.openai.com/docs)
- [SQLAlchemy 2.x](https://docs.sqlalchemy.org/20/)

## Observações

- Em produção, Swagger UI está desativado (`app_env=production`)
- Autenticação é stateless via JWT do Supabase
- Frontend refaz login automaticamente se token expirar
- Backend valida JWT via JWKS do Supabase (não armazena secrets)
- Alembic migrations rodadas automaticamente em startup (dev) ou manual (prod)
