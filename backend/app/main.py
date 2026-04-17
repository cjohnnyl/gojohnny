from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address

from .core.config import get_settings

settings = get_settings()


def _get_user_id_from_token(request: Request) -> str:
    """Extrai user_id do JWT Supabase para usar como chave de rate limiting por usuário.
    Cai de volta para o IP caso o token não esteja presente, seja inválido ou o
    JWKS não esteja disponível (falha silenciosa intencional — rate limit por IP).
    """
    from .services.deps import _decode_jwt_with_jwks
    from fastapi import HTTPException

    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        token = auth_header[7:]
        try:
            payload = _decode_jwt_with_jwks(token)
            user_id = payload.get("sub")
            if user_id:
                return f"user:{user_id}"
        except (HTTPException, Exception):
            pass
    # fallback para IP
    return get_remote_address(request)


limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Iniciando {settings.app_name} v{settings.app_version} [{settings.app_env}]")
    # Cria tabelas no banco (dev). Em produção, use Alembic migrations.
    if settings.app_env == "development":
        from .core.database import engine, Base
        Base.metadata.create_all(bind=engine)
        logger.info("Tabelas verificadas/criadas (modo desenvolvimento)")
    yield
    logger.info("Encerrando aplicação")


# Desabilita docs em produção
_docs_url = None if settings.app_env == "production" else "/docs"
_redoc_url = None if settings.app_env == "production" else "/redoc"
_openapi_url = None if settings.app_env == "production" else "/openapi.json"

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="GoJohnny — Seu treinador digital de corrida de rua",
    docs_url=_docs_url,
    redoc_url=_redoc_url,
    openapi_url=_openapi_url,
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)


@app.get("/", tags=["health"])
def root():
    response = {
        "app": settings.app_name,
        "version": settings.app_version,
        "status": "ok",
    }
    if settings.app_env != "production":
        response["env"] = settings.app_env
    return response


@app.get("/health", tags=["health"])
def health():
    return {"status": "ok"}


from .routes import chat, feedback, plans, profile, memory

app.include_router(profile.router, prefix="/profile", tags=["profile"])
app.include_router(chat.router, prefix="/chat", tags=["chat"])
app.include_router(plans.router, prefix="/plans", tags=["plans"])
app.include_router(feedback.router, prefix="/feedback", tags=["feedback"])
app.include_router(memory.router, prefix="/memory", tags=["memory"])
