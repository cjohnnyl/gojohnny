from pathlib import Path
from functools import lru_cache
from pydantic_settings import BaseSettings

# Localiza o .env na raiz do projeto (dois níveis acima de app/core/)
_ROOT = Path(__file__).resolve().parents[3]
_ENV_FILE = _ROOT / ".env"


class Settings(BaseSettings):
    # App
    app_env: str = "development"
    app_debug: bool = True
    app_name: str = "GoJohnny"
    app_version: str = "0.1.0"

    # Database
    database_url: str = "sqlite:///./gojohnny.db"

    # JWT
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 60
    jwt_refresh_token_expire_days: int = 30

    # Anthropic
    anthropic_api_key: str
    anthropic_model_chat: str = "claude-haiku-4-5-20251001"
    anthropic_model_coach: str = "claude-sonnet-4-6"
    anthropic_max_tokens: int = 2048

    # Observability
    log_level: str = "INFO"
    sentry_dsn: str = ""

    # CORS
    allowed_origins: str = "http://localhost:3000,http://localhost:8000"

    @property
    def allowed_origins_list(self) -> list[str]:
        return [o.strip() for o in self.allowed_origins.split(",")]

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"

    class Config:
        env_file = str(_ENV_FILE)
        env_file_encoding = "utf-8"


@lru_cache
def get_settings() -> Settings:
    return Settings()
