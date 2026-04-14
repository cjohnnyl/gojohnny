from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from .core.config import get_settings
from .core.database import engine, Base

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Iniciando {settings.app_name} v{settings.app_version} [{settings.app_env}]")
    # Cria tabelas no banco (dev). Em produção, use Alembic migrations.
    if settings.app_env == "development":
        Base.metadata.create_all(bind=engine)
        logger.info("Tabelas verificadas/criadas (modo desenvolvimento)")
    yield
    logger.info("Encerrando aplicação")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="GoJohnny — Seu treinador digital de corrida de rua",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["health"])
def root():
    return {
        "app": settings.app_name,
        "version": settings.app_version,
        "status": "ok",
        "env": settings.app_env,
    }


@app.get("/health", tags=["health"])
def health():
    return {"status": "ok"}


from .routes import auth, chat, feedback, plans, profile

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(profile.router, prefix="/profile", tags=["profile"])
app.include_router(chat.router, prefix="/chat", tags=["chat"])
app.include_router(plans.router, prefix="/plans", tags=["plans"])
app.include_router(feedback.router, prefix="/feedback", tags=["feedback"])
