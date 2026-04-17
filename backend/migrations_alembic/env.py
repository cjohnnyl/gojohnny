from logging.config import fileConfig
import sys
import os

from sqlalchemy import engine_from_config
from sqlalchemy import pool
from sqlalchemy import text, inspect as sa_inspect
from alembic import context

# Adiciona o backend ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.core.config import get_settings
from app.core.database import Base
import app.models  # noqa: F401 — registra todos os models

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

settings = get_settings()

# Normaliza o DATABASE_URL para usar o driver psycopg3 (mesmo padrão do database.py)
_db_url = settings.database_url
if _db_url.startswith("postgresql://"):
    _db_url = _db_url.replace("postgresql://", "postgresql+psycopg://", 1)
elif _db_url.startswith("postgres://"):
    _db_url = _db_url.replace("postgres://", "postgresql+psycopg://", 1)

config.set_main_option("sqlalchemy.url", _db_url)

target_metadata = Base.metadata


def _maybe_stamp_existing_db(connection) -> None:
    """
    Estabiliza banco em estado inconsistente (tabelas existem sem rastreamento Alembic).
    Registra '0001' no alembic_version para que o Alembic pule direto para '0002'.
    """
    try:
        inspector = sa_inspect(connection)
        tables = inspector.get_table_names(schema="public")

        if "runner_profiles" not in tables:
            return  # banco vazio — Alembic cuida normalmente

        # Tabelas existem. Garantir que alembic_version existe e tem '0001'.
        if "alembic_version" not in tables:
            connection.execute(text(
                "CREATE TABLE alembic_version "
                "(version_num VARCHAR(32) NOT NULL "
                "CONSTRAINT alembic_version_pkc PRIMARY KEY)"
            ))
            connection.execute(text("INSERT INTO alembic_version (version_num) VALUES ('0001')"))
            connection.commit()
            print("[pre-migration] alembic_version criada e registrada em 0001")
            return

        result = connection.execute(text("SELECT version_num FROM alembic_version"))
        if not result.fetchall():
            connection.execute(text("INSERT INTO alembic_version (version_num) VALUES ('0001')"))
            connection.commit()
            print("[pre-migration] alembic_version vazia — registrada em 0001")

    except Exception as exc:
        print(f"[pre-migration] Verificação ignorada: {exc}")


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        _maybe_stamp_existing_db(connection)   # ← estabiliza banco inconsistente antes de migrar

        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
