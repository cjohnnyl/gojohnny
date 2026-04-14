# GoJohnny

Seu treinador digital de corrida de rua.

GoJohnny é um chatbot especialista em corrida que funciona como um treinador pessoal digital — com acompanhamento contínuo, personalizado e baseado no contexto real do corredor.

---

## O que o GoJohnny faz

- Gera planilhas de treino personalizadas por semana
- Analisa feedback pós-treino e adapta recomendações futuras
- Prepara estratégia de prova (5K, 10K, 21K)
- Orienta alimentação pré e pós-treino
- Responde dúvidas sobre treino, clima, equipamentos e rotina de corrida
- Mantém memória de contexto para continuidade do acompanhamento

---

## Stack

- **Backend:** Python 3.11+ + FastAPI
- **Banco:** SQLite (dev) → PostgreSQL (prod)
- **ORM:** SQLAlchemy 2.x + Alembic
- **Auth:** JWT (python-jose + passlib)
- **IA:** Anthropic Claude API
- **Hosting:** Railway

---

## Setup local

```bash
# 1. Clonar o repositório
git clone <repo-url>
cd gojohnny

# 2. Criar virtualenv
python -m venv .venv
.venv\Scripts\activate       # Windows
# source .venv/bin/activate  # Linux/Mac

# 3. Instalar dependências
pip install -r backend/requirements.txt

# 4. Configurar variáveis de ambiente
cp .env.example .env
# Edite .env com suas chaves (ANTHROPIC_API_KEY e JWT_SECRET_KEY são obrigatórias)

# 5. Rodar
cd backend
uvicorn app.main:app --reload --port 8000
```

Acesse a documentação interativa: http://localhost:8000/docs

---

## Documentação

- [Arquitetura inicial](docs/arquitetura-inicial.md)
- [Banco de dados](docs/banco-de-dados.md)
- [Estratégia de deploy](docs/deploy.md)

---

## Guardrails

O GoJohnny não diagnostica lesões, não prescreve tratamento médico e não substitui profissionais de saúde.
Em situações de dor forte ou sinais de risco, orienta o usuário a buscar atendimento especializado.

---

## Status

MVP em desenvolvimento. Interface atual: API REST com Swagger UI.
