import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_current_user_opcional
from app.core.security import decode_token
from app.database import get_db
from app.model.usuario import Usuario
from app.schemas.auth_schema import (
    AlterarSenhaRequest,
    LoginRequest,
    RefreshRequest,
    Token,
)
from app.schemas.common import Mensagem
from app.schemas.usuario_schema import UsuarioCreate, UsuarioResponse
from app.services import auth_service, usuario_service

router = APIRouter(prefix="/api/auth", tags=["Autenticação"])


@router.post("/registrar", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
def registrar(
    dados: UsuarioCreate,
    db: Session = Depends(get_db),
    usuario_atual: Usuario | None = Depends(get_current_user_opcional),
):
    return auth_service.registrar(db, dados, usuario_atual)


@router.post("/login", response_model=Token)
def login(dados: LoginRequest, db: Session = Depends(get_db)):
    return auth_service.login(db, dados.email, dados.senha)


@router.post("/token", response_model=Token)
def token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    return auth_service.login(db, form_data.username, form_data.password)


@router.post("/refresh", response_model=Token)
def refresh(dados: RefreshRequest, db: Session = Depends(get_db)):
    try:
        payload = decode_token(dados.refresh_token, tipo_esperado="refresh")
        usuario_id = int(payload["sub"])
    except (jwt.PyJWTError, KeyError, TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token inválido ou expirado",
        )

    usuario = db.get(Usuario, usuario_id)
    if not usuario or not usuario.ativo:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário não encontrado ou inativo",
        )
    return auth_service.montar_tokens(usuario)


@router.get("/me", response_model=UsuarioResponse)
def me(usuario: Usuario = Depends(get_current_user)):
    return usuario


@router.post("/alterar-senha", response_model=Mensagem)
def alterar_senha(
    dados: AlterarSenhaRequest,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    usuario_service.alterar_senha(db, usuario, dados.senha_atual, dados.nova_senha)
    return Mensagem(mensagem="Senha alterada com sucesso")
