# Estratégia de Deploy — GoJohnny MVP

**Data:** 2026-04-13

---

## Ambiente de desenvolvimento

```bash
# 1. Clonar o repositório
cd C:\Projetos\gojohnny

# 2. Criar e ativar virtualenv
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # Linux/Mac

# 3. Instalar dependências
pip install -r backend/requirements.txt

# 4. Configurar variáveis de ambiente
cp .env.example .env
# Editar .env com as chaves necessárias

# 5. Rodar a aplicação
cd backend
uvicorn app.main:app --reload --port 8000
```

Acesse: http://localhost:8000/docs

---

## Produção — Railway

### Por que Railway?

- Suporte nativo a Python (Nixpacks detecta automaticamente)
- Postgres gerenciado no mesmo projeto
- Deploy por push no GitHub
- Free tier adequado para MVP
- `DATABASE_URL` injetado automaticamente pelo Railway

### Passos para o primeiro deploy

**1. Criar conta e projeto**
- Acesse railway.app
- Crie um novo projeto
- Conecte o repositório GitHub

**2. Adicionar banco de dados**
- No projeto Railway, clique em "New" → "Database" → "PostgreSQL"
- Railway injeta `DATABASE_URL` automaticamente

**3. Configurar variáveis de ambiente**
No painel Railway → Settings → Variables, adicionar:
```
APP_ENV=production
APP_DEBUG=false
JWT_SECRET_KEY=<gerar com python -c "import secrets; print(secrets.token_hex(32))">
ANTHROPIC_API_KEY=<sua chave>
ANTHROPIC_MODEL_CHAT=claude-haiku-4-5-20251001
ANTHROPIC_MODEL_COACH=claude-sonnet-4-6
LOG_LEVEL=INFO
```

**4. Arquivo de configuração do Railway**
Criar `railway.json` na raiz do projeto:
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 3
  }
}
```

**5. Migrations em produção**
Em produção, não usar `Base.metadata.create_all`.
Usar Alembic:
```bash
alembic upgrade head
```

---

## Variáveis obrigatórias por ambiente

| Variável | Dev | Prod |
|----------|-----|------|
| `DATABASE_URL` | SQLite (padrão) | Postgres (Railway injeta) |
| `JWT_SECRET_KEY` | Pode ser simples | Obrigatório seguro |
| `ANTHROPIC_API_KEY` | Obrigatório | Obrigatório |
| `APP_ENV` | development | production |
| `SENTRY_DSN` | Opcional | Recomendado |

---

## Custo estimado do MVP

| Serviço | Plano | Custo mensal |
|---------|-------|-------------|
| Railway (backend + Postgres) | Hobby | ~$5 USD |
| Anthropic Claude API | Pay as you go | ~$1–10 USD (depende do uso) |
| **Total estimado** | | **~$6–15 USD/mês** |

Referência de custo da API:
- `claude-haiku-4-5`: $0.80/M tokens input, $4/M tokens output
- `claude-sonnet-4-6`: $3/M tokens input, $15/M tokens output
