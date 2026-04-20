"""Dependências compartilhadas do FastAPI."""
from functools import lru_cache

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from loguru import logger
from supabase import Client, create_client

from ..core.config import get_settings

bearer = HTTPBearer()


@lru_cache(maxsize=1)
def _get_supabase_client() -> Client:
    settings = get_settings()
    if not settings.supabase_url or not settings.supabase_anon_key:
        raise RuntimeError("SUPABASE_URL ou SUPABASE_ANON_KEY não configuradas")
    return create_client(settings.supabase_url, settings.supabase_anon_key)


async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
) -> str:
    token = credentials.credentials
    try:
        client = _get_supabase_client()
        response = client.auth.get_user(token)
        if response.user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido",
            )
        return response.user.id
    except HTTPException:
        raise
    except Exception as exc:
        logger.warning(f"Falha ao validar token: {type(exc).__name__}: {exc}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
        )
