from datetime import datetime, timedelta, timezone
from typing import Any

import bcrypt
import jwt

from app.core.config import get_settings


def hash_password(senha: str) -> str:
    return bcrypt.hashpw(senha.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(senha: str, senha_hash: str) -> bool:
    if not senha or not senha_hash:
        return False
    try:
        return bcrypt.checkpw(senha.encode("utf-8"), senha_hash.encode("utf-8"))
    except (ValueError, TypeError):
        return False


def _criar_token(subject: str, tipo: str, expira_em: timedelta, extra: dict[str, Any] | None = None) -> str:
    settings = get_settings()
    agora = datetime.now(timezone.utc)
    payload: dict[str, Any] = {
        "sub": str(subject),
        "tipo": tipo,
        "iat": agora,
        "exp": agora + expira_em,
    }
    if extra:
        payload.update(extra)
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


def create_access_token(subject: str, extra: dict[str, Any] | None = None) -> str:
    settings = get_settings()
    return _criar_token(
        subject,
        tipo="access",
        expira_em=timedelta(minutes=settings.access_token_expire_minutes),
        extra=extra,
    )


def create_refresh_token(subject: str) -> str:
    settings = get_settings()
    return _criar_token(
        subject,
        tipo="refresh",
        expira_em=timedelta(days=settings.refresh_token_expire_days),
    )


def decode_token(token: str, tipo_esperado: str | None = None) -> dict[str, Any]:
    settings = get_settings()
    payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
    if tipo_esperado and payload.get("tipo") != tipo_esperado:
        raise jwt.InvalidTokenError("Tipo de token inválido")
    return payload
