"""Dependências compartilhadas do FastAPI."""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt, JWTError
from loguru import logger

from ..core.config import get_settings

settings = get_settings()
bearer = HTTPBearer()


async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
) -> str:
    """
    Valida JWT emitido pelo Supabase Auth e retorna o user_id (UUID).
    O JWT é verificado com o JWT_SECRET do projeto Supabase.
    """
    token = credentials.credentials

    if not settings.supabase_jwt_secret:
        logger.error("SUPABASE_JWT_SECRET não configurado")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Configuração de autenticação incompleta",
        )

    try:
        payload = jwt.decode(
            token,
            settings.supabase_jwt_secret,
            algorithms=["HS256"],
            options={"verify_aud": False},  # Supabase emite com audience "authenticated"
        )
        user_id: str = payload.get("sub")
        if not user_id:
            logger.warning("Token válido mas sem 'sub' claim")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido",
            )
        return user_id
    except JWTError as e:
        logger.warning(f"Erro ao decodificar JWT: {type(e).__name__}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado",
        )
