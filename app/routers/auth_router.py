"""Router de autenticação e sessão de usuários.

Concentra o registro de usuários, login por JSON e por formulário OAuth2,
renovação de tokens, consulta do usuário autenticado e troca de senha.

Endpoints expostos (prefixo ``/api/auth``):
- ``POST /registrar``     -> cria usuário (com ou sem autenticação);
- ``POST /login``         -> login via JSON (e-mail + senha);
- ``POST /token``         -> login via formulário OAuth2 (compatível com docs);
- ``POST /refresh``       -> renova o par de tokens usando refresh token;
- ``GET /me``             -> dados do usuário autenticado;
- ``POST /alterar-senha`` -> troca de senha do usuário autenticado.
"""

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

# Prefixo e tag OpenAPI comuns a todas as rotas de autenticação.
router = APIRouter(prefix="/api/auth", tags=["Autenticação"])


@router.post("/registrar", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
def registrar(
    dados: UsuarioCreate,
    db: Session = Depends(get_db),
    usuario_atual: Usuario | None = Depends(get_current_user_opcional),
):
    """Registra um novo usuário.

    A dependência ``get_current_user_opcional`` permite que a rota seja usada
    tanto de forma pública quanto por um usuário já autenticado; nesse caso o
    ``usuario_atual`` é repassado ao serviço para aplicar regras de permissão
    (por exemplo, definir perfil).

    Parâmetros:
    - ``dados``: payload de criação do usuário (``UsuarioCreate``).

    Retorno: ``UsuarioResponse`` do usuário criado (HTTP 201).
    """
    return auth_service.registrar(db, dados, usuario_atual)


@router.post("/login", response_model=Token)
def login(dados: LoginRequest, db: Session = Depends(get_db)):
    """Autentica por e-mail e senha informados no corpo JSON.

    Retorno: ``Token`` com access token, refresh token e metadados; as falhas
    de credenciais são tratadas pelo serviço (HTTP 401).
    """
    return auth_service.login(db, dados.email, dados.senha)


# Variante OAuth2 usada pelo botão "Authorize" da documentação automática.
@router.post("/token", response_model=Token)
def token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """Autentica via formulário OAuth2 (``username``/``password``).

    O campo ``username`` recebe o e-mail do usuário. Retorno: ``Token``.
    """
    return auth_service.login(db, form_data.username, form_data.password)


@router.post("/refresh", response_model=Token)
def refresh(dados: RefreshRequest, db: Session = Depends(get_db)):
    """Gera um novo par de tokens a partir de um refresh token válido.

    Valida o JWT exigindo que seja do tipo ``refresh`` e extrai o id do usuário
    do campo ``sub``. Se o token for inválido/expirado ou o usuário não existir
    (ou estiver inativo), responde HTTP 401.

    Retorno: ``Token`` renovado.
    """
    try:
        # Decodifica o token garantindo que ele seja especificamente de refresh.
        payload = decode_token(dados.refresh_token, tipo_esperado="refresh")
        usuario_id = int(payload["sub"])
    except (jwt.PyJWTError, KeyError, TypeError, ValueError):
        # Erros de assinatura/expiração ou payload malformado viram 401.
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token inválido ou expirado",
        )

    usuario = db.get(Usuario, usuario_id)
    # Impede renovação para usuários removidos ou desativados.
    if not usuario or not usuario.ativo:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário não encontrado ou inativo",
        )
    return auth_service.montar_tokens(usuario)


@router.get("/me", response_model=UsuarioResponse)
def me(usuario: Usuario = Depends(get_current_user)):
    """Retorna os dados do usuário autenticado.

    Autenticação: obrigatória (o usuário é resolvido pelo token).
    Retorno: ``UsuarioResponse`` do próprio usuário.
    """
    return usuario


@router.post("/alterar-senha", response_model=Mensagem)
def alterar_senha(
    dados: AlterarSenhaRequest,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    """Altera a senha do usuário autenticado.

    Valida a senha atual e aplica a nova senha por meio do serviço.
    Autenticação: obrigatória.
    Retorno: ``Mensagem`` de confirmação.
    """
    usuario_service.alterar_senha(db, usuario, dados.senha_atual, dados.nova_senha)
    return Mensagem(mensagem="Senha alterada com sucesso")
