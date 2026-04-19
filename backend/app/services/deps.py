"""Dependências compartilhadas do FastAPI."""
from functools import lru_cache

import jwt as pyjwt
from jwt import PyJWKClient
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from loguru import logger

from ..core.config import get_settings

bearer = HTTPBearer()


@lru_cache(maxsize=1)
def _get_jwks_client() -> PyJWKClient:
    settings = get_settings()
    if not settings.supabase_url:
        raise RuntimeError("SUPABASE_URL não configurada")
    base = settings.supabase_url.rstrip("/")
    jwks_url = f"{base}/auth/v1/.well-known/jwks.json"
    return PyJWKClient(jwks_url, cache_jwk_set=True, lifespan=300)


def _decode_jwt_with_jwks(token: str) -> dict:
    try:
        client = _get_jwks_client()
        signing_key = client.get_signing_key_from_jwt(token)
        payload = pyjwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            options={"verify_aud": False},
        )
        return payload
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expirado",
        )
    except Exception as exc:
        logger.warning(f"Falha ao validar token JWT: {type(exc).__name__}: {exc}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
        )


async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
) -> str:
    token = credentials.credentials
    payload = _decode_jwt_with_jwks(token)

    user_id: str | None = payload.get("sub")
    if not user_id:
        logger.warning("Token RS256 válido mas sem claim 'sub'")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido: identificador de usuário ausente",
        )

    return user_id
