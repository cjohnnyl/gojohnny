"""Dependências compartilhadas do FastAPI."""
import json
import urllib.request
from functools import lru_cache

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt, JWTError
from jose.exceptions import ExpiredSignatureError
from loguru import logger

from ..core.config import get_settings

bearer = HTTPBearer()


@lru_cache(maxsize=1)
def _get_jwks_url() -> str:
    """Retorna a URL do endpoint JWKS do Supabase."""
    settings = get_settings()
    if not settings.supabase_url:
        raise RuntimeError("SUPABASE_URL não configurada")
    base = settings.supabase_url.rstrip("/")
    return f"{base}/auth/v1/.well-known/jwks.json"


def _fetch_jwks() -> dict:
    """
    Busca as chaves públicas JWKS do Supabase.
    Erros de rede resultam em HTTP 503 para o cliente.
    """
    url = _get_jwks_url()
    try:
        with urllib.request.urlopen(url, timeout=5) as response:
            return json.loads(response.read().decode())
    except Exception as exc:
        logger.error(f"Falha ao buscar JWKS em {url}: {exc}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Serviço de autenticação temporariamente indisponível",
        )


def _decode_jwt_with_jwks(token: str) -> dict:
    """
    Decodifica e valida um JWT RS256 usando as chaves públicas JWKS do Supabase.

    - Busca o JWKS dinâmico (sem cache em memória para garantir rotação de chaves)
    - Tenta cada chave até encontrar a que valida o token
    - Aceita audience 'authenticated' emitida pelo Supabase
    """
    jwks = _fetch_jwks()
    keys = jwks.get("keys", [])

    if not keys:
        logger.error("JWKS retornou lista de chaves vazia")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Serviço de autenticação com configuração inválida",
        )

    last_error: Exception | None = None
    for jwk in keys:
        try:
            payload = jwt.decode(
                token,
                jwk,
                algorithms=["RS256"],
                options={"verify_aud": False},  # Supabase emite audience "authenticated"
            )
            return payload
        except ExpiredSignatureError:
            # Token expirado — não adianta tentar outras chaves
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expirado",
            )
        except JWTError as exc:
            last_error = exc
            continue

    logger.warning(f"Nenhuma chave JWKS validou o token: {type(last_error).__name__}")
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token inválido",
    )


async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
) -> str:
    """
    Valida JWT emitido pelo Supabase Auth via JWKS (RS256) e retorna o user_id (UUID).

    Fluxo:
    1. Extrai o Bearer token do header Authorization
    2. Busca as chaves públicas no endpoint JWKS do Supabase
    3. Decodifica e valida a assinatura RS256
    4. Retorna o claim 'sub' (UUID do usuário)
    """
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
