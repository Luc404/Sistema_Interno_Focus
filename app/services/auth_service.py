from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.security import create_access_token, create_refresh_token
from app.model.usuario import Usuario
from app.schemas.auth_schema import Token
from app.schemas.usuario_schema import UsuarioCreate
from app.services import usuario_service


def montar_tokens(usuario: Usuario) -> Token:
    settings = get_settings()
    return Token(
        access_token=create_access_token(str(usuario.id), extra={"perfil": usuario.perfil}),
        refresh_token=create_refresh_token(str(usuario.id)),
        expires_in=settings.access_token_expire_minutes * 60,
    )


def login(db: Session, email: str, senha: str) -> Token:
    usuario = usuario_service.autenticar(db, email, senha)
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha inválidos",
        )
    if not usuario.ativo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário inativo",
        )
    return montar_tokens(usuario)


def registrar(db: Session, dados: UsuarioCreate, criador: Usuario | None = None) -> Usuario:
    total_usuarios = db.query(Usuario).count()
    if total_usuarios > 0:
        if criador is None or criador.perfil != "ADMIN":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Somente administradores podem cadastrar novos usuários",
            )
    else:
        dados.perfil = "ADMIN"

    return usuario_service.criar_usuario(db, dados)


def criar_admin_inicial(db: Session) -> None:
    settings = get_settings()
    if not settings.first_admin_email or not settings.first_admin_password:
        return
    if db.query(Usuario).count() > 0:
        return
    dados = UsuarioCreate(
        nome_completo=settings.first_admin_nome,
        email=settings.first_admin_email,
        senha=settings.first_admin_password,
        perfil="ADMIN",
    )
    usuario_service.criar_usuario(db, dados)
