"""Dependências compartilhadas do FastAPI.

Concentra a autenticação via JWT, a obtenção do usuário atual e as
verificações de perfil e de propriedade de recursos.
"""

from collections.abc import Callable

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.security import decode_token
from app.database import get_db
from app.model.usuario import Usuario

# Esquemas OAuth2: um obrigatório para rotas protegidas e outro opcional
# para rotas que se comportam de forma diferente com ou sem autenticação.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")
oauth2_scheme_opcional = OAuth2PasswordBearer(tokenUrl="/api/auth/token", auto_error=False)

CREDENCIAIS_INVALIDAS = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Credenciais inválidas ou expiradas",
    headers={"WWW-Authenticate": "Bearer"},
)


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> Usuario:
    """Valida o token de acesso e retorna o usuário autenticado ativo."""
    try:
        payload = decode_token(token, tipo_esperado="access")
        usuario_id = int(payload["sub"])
    except (jwt.PyJWTError, KeyError, TypeError, ValueError):
        raise CREDENCIAIS_INVALIDAS

    usuario = db.get(Usuario, usuario_id)
    if not usuario:
        raise CREDENCIAIS_INVALIDAS
    if not usuario.ativo:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Usuário inativo")
    return usuario


def get_current_user_opcional(
    token: str | None = Depends(oauth2_scheme_opcional),
    db: Session = Depends(get_db),
) -> Usuario | None:
    """Retorna o usuário autenticado quando houver token válido, ou None."""
    if not token:
        return None
    try:
        payload = decode_token(token, tipo_esperado="access")
        usuario_id = int(payload["sub"])
    except (jwt.PyJWTError, KeyError, TypeError, ValueError):
        return None

    usuario = db.get(Usuario, usuario_id)
    if not usuario or not usuario.ativo:
        return None
    return usuario


def require_perfis(*perfis: str) -> Callable:
    """Cria uma dependência que exige que o usuário tenha um dos perfis informados."""

    def verificador(usuario: Usuario = Depends(get_current_user)) -> Usuario:
        """Verifica se o perfil do usuário está entre os perfis permitidos."""
        if usuario.perfil not in perfis:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Você não tem permissão para executar esta ação",
            )
        return usuario

    return verificador


def ensure_owner_or_admin(usuario: Usuario, proprietario_id: int | None) -> None:
    """Garante que o usuário seja administrador ou o proprietário do recurso."""
    if usuario.perfil != "ADMIN" and usuario.id != proprietario_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não tem permissão para acessar este recurso",
        )
