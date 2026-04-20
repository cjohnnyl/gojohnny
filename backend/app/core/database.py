from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from .config import get_settings


class Base(DeclarativeBase):
    pass


def _build_engine():
    settings = get_settings()
    database_url = settings.database_url

    connect_args = {}
    if database_url.startswith("sqlite"):
        connect_args = {"check_same_thread": False}
    elif database_url.startswith("postgresql://") or database_url.startswith("postgres://"):
        database_url = database_url.replace("postgresql://", "postgresql+psycopg://", 1)
        database_url = database_url.replace("postgres://", "postgresql+psycopg://", 1)

    _engine = create_engine(
        database_url,
        connect_args=connect_args,
        echo=settings.app_debug,
    )

    if database_url.startswith("sqlite"):
        @event.listens_for(_engine, "connect")
        def set_sqlite_pragma(dbapi_conn, _):
            cursor = dbapi_conn.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

    return _engine


_engine_cache = None
_session_cache = None


def get_engine():
    global _engine_cache
    if _engine_cache is None:
        _engine_cache = _build_engine()
    return _engine_cache


def get_session_factory():
    global _session_cache
    if _session_cache is None:
        _session_cache = sessionmaker(autocommit=False, autoflush=False, bind=get_engine())
    return _session_cache


def get_db():
    db = get_session_factory()()
    try:
        yield db
    finally:
        db.close()
