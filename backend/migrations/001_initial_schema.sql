-- =============================================================================
-- GoJohnny — Migration 001: Schema Inicial
-- =============================================================================
-- Banco alvo: SQLite (dev) | PostgreSQL (prod)
-- Executar na ordem abaixo para respeitar dependências de FK.
-- =============================================================================

-- Habilitar foreign keys no SQLite
PRAGMA foreign_keys = ON;

-- -----------------------------------------------------------------------------
-- Tabela: users
-- Propósito: identidade e autenticação do corredor
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS users (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    email       TEXT    NOT NULL UNIQUE,
    password_hash TEXT  NOT NULL,
    is_active   INTEGER NOT NULL DEFAULT 1,       -- 1 = ativo, 0 = inativo
    created_at  TEXT    NOT NULL DEFAULT (datetime('now')),
    updated_at  TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

-- -----------------------------------------------------------------------------
-- Tabela: runner_profiles
-- Propósito: contexto do corredor — alimenta todas as recomendações
-- Campos críticos para MVP: name, level, weekly_volume_km, available_days_per_week
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS runner_profiles (
    id                      INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id                 INTEGER NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,

    -- Identificação
    name                    TEXT    NOT NULL,

    -- Nível: beginner | intermediate | advanced
    level                   TEXT    NOT NULL DEFAULT 'beginner',

    -- Volume e disponibilidade
    weekly_volume_km        REAL,
    available_days_per_week INTEGER NOT NULL DEFAULT 3,
    preferred_days          TEXT,                 -- ex: "seg,qua,sex"

    -- Pace confortável (min/km) — ex: "6:30"
    comfortable_pace        TEXT,

    -- Objetivo: complete_5k | complete_10k | complete_21k | improve_time | consistency | other
    main_goal               TEXT,

    -- Prova alvo
    target_race_name        TEXT,
    target_race_distance_km REAL,
    target_race_date        TEXT,                 -- ISO 8601: "2026-06-15"

    -- Histórico e limitações (texto livre)
    injury_history          TEXT,
    physical_limitations    TEXT,

    -- Localização (cidade/estado)
    location                TEXT,

    -- Contexto livre adicional
    extra_context           TEXT,

    created_at  TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at  TEXT NOT NULL DEFAULT (datetime('now'))
);

-- -----------------------------------------------------------------------------
-- Tabela: training_plans
-- Propósito: planilhas semanais geradas pelo GoJohnny
-- plan_data: JSON com a estrutura da semana
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS training_plans (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id          INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    week_start       TEXT    NOT NULL,            -- ISO 8601: "2026-04-14"
    week_end         TEXT    NOT NULL,            -- ISO 8601: "2026-04-20"

    -- JSON: [ { "day": "seg", "type": "leve", "km": 5, "pace": "6:30", "notes": "..." }, ... ]
    plan_data        TEXT    NOT NULL,

    -- Snapshot do contexto usado na geração (rastreabilidade)
    context_snapshot TEXT,                        -- JSON

    -- active | superseded | archived
    status           TEXT    NOT NULL DEFAULT 'active',

    coach_notes      TEXT,

    generated_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at   TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_training_plans_user_id ON training_plans(user_id);
CREATE INDEX IF NOT EXISTS idx_training_plans_week_start ON training_plans(week_start);

-- -----------------------------------------------------------------------------
-- Tabela: training_feedbacks
-- Propósito: feedback pós-treino — informa adaptações futuras
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS training_feedbacks (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id             INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    plan_id             INTEGER REFERENCES training_plans(id) ON DELETE SET NULL,

    training_date       TEXT    NOT NULL,         -- ISO 8601

    -- Percepção de esforço (1-10)
    effort_rating       INTEGER CHECK(effort_rating BETWEEN 1 AND 10),

    -- Dor/desconforto (0 = nenhum, 10 = intenso)
    pain_level          INTEGER CHECK(pain_level BETWEEN 0 AND 10),

    -- Qualidade do sono (1-5)
    sleep_quality       INTEGER CHECK(sleep_quality BETWEEN 1 AND 5),

    -- Sensação geral: great | good | ok | bad | very_bad
    general_feeling     TEXT    CHECK(general_feeling IN ('great', 'good', 'ok', 'bad', 'very_bad')),

    -- Notas livres do usuário
    notes               TEXT,

    -- Análise gerada pelo GoJohnny
    ai_analysis         TEXT,

    -- maintain | reduce | increase
    load_recommendation TEXT    CHECK(load_recommendation IN ('maintain', 'reduce', 'increase')),

    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_feedbacks_user_id ON training_feedbacks(user_id);
CREATE INDEX IF NOT EXISTS idx_feedbacks_training_date ON training_feedbacks(training_date);

-- -----------------------------------------------------------------------------
-- Tabela: conversations
-- Propósito: sessões de conversa com o chatbot
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS conversations (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id    INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title      TEXT,                              -- gerado automaticamente
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_conversations_user_id ON conversations(user_id);

-- -----------------------------------------------------------------------------
-- Tabela: messages
-- Propósito: histórico de mensagens de cada conversa
-- role: user | assistant | system
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS messages (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    conversation_id INTEGER NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,

    -- user | assistant | system
    role            TEXT    NOT NULL CHECK(role IN ('user', 'assistant', 'system')),

    content         TEXT    NOT NULL,

    -- Controle de custo
    tokens_used     INTEGER,
    model_used      TEXT,

    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX IF NOT EXISTS idx_messages_created_at ON messages(created_at);

-- =============================================================================
-- Fim da migration 001
-- =============================================================================
