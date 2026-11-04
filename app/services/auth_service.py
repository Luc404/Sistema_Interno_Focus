"""Serviço de autenticação e cadastro de usuários.

Responsável por montar os tokens JWT de acesso/refresh, validar credenciais
de login, controlar quem pode registrar novos usuários e criar o primeiro
administrador a partir das configurações da aplicação.
"""

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.security import create_access_token, create_refresh_token
from app.model.usuario import Usuario
from app.schemas.auth_schema import Token
from app.schemas.usuario_schema import UsuarioCreate
from app.services import usuario_service


def montar_tokens(usuario: Usuario) -> Token:
    """Gera o par de tokens JWT (acesso e refresh) para um usuário.

    Args:
        usuario: Instância do usuário autenticado.

    Returns:
        Um schema ``Token`` contendo access_token, refresh_token e o tempo de
        expiração do access token em segundos.

    Raises:
        Nenhuma exceção de negócio; falhas na geração dos tokens são propagadas.
    """
    settings = get_settings()
    return Token(
        # O subject do JWT é o ID do usuário; o perfil vai como claim extra
        # para permitir autorização sem consultar o banco a cada requisição.
        access_token=create_access_token(str(usuario.id), extra={"perfil": usuario.perfil}),
        refresh_token=create_refresh_token(str(usuario.id)),
        # Converte o tempo de expiração de minutos para segundos.
        expires_in=settings.access_token_expire_minutes * 60,
    )


def login(db: Session, email: str, senha: str) -> Token:
    """Autentica um usuário por e-mail e senha e devolve os tokens.

    Args:
        db: Sessão do SQLAlchemy.
        email: E-mail informado no login.
        senha: Senha em texto plano informada no login.

    Returns:
        Um schema ``Token`` com os tokens JWT do usuário autenticado.

    Raises:
        HTTPException: 401 quando as credenciais são inválidas e 403 quando o
            usuário existe, mas está inativo.
    """
    # autenticar valida a senha contra o hash armazenado.
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
    """Registra um novo usuário respeitando a regra do primeiro administrador.

    Enquanto não houver nenhum usuário no sistema, o primeiro cadastro pode ser
    feito sem autenticação e é forçado a perfil ``ADMIN``. Depois disso, apenas
    um administrador autenticado pode criar novos usuários.

    Args:
        db: Sessão do SQLAlchemy.
        dados: Dados do usuário a ser criado.
        criador: Usuário autenticado que está executando o cadastro (opcional).

    Returns:
        O usuário criado.

    Raises:
        HTTPException: 403 quando já existem usuários e o criador não é ADMIN.
    """
    # Verifica se o sistema já possui usuários cadastrados.
    total_usuarios = db.query(Usuario).count()
    if total_usuarios > 0:
        # A partir do segundo usuário, exige um criador com perfil ADMIN.
        if criador is None or criador.perfil != "ADMIN":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Somente administradores podem cadastrar novos usuários",
            )
    else:
        # Bootstrap: o primeiro usuário do sistema sempre nasce administrador.
        dados.perfil = "ADMIN"

    return usuario_service.criar_usuario(db, dados)


def criar_admin_inicial(db: Session) -> None:
    """Cria o administrador inicial definido nas configurações, se necessário.

    A criação só ocorre quando e-mail e senha estão configurados e ainda não
    existe nenhum usuário no banco, evitando duplicidade em reinicializações.

    Args:
        db: Sessão do SQLAlchemy.

    Returns:
        ``None``.

    Raises:
        Erros de banco/criação são propagados pelo serviço de usuários.
    """
    settings = get_settings()
    # Sem credenciais configuradas não há bootstrap a fazer.
    if not settings.first_admin_email or not settings.first_admin_password:
        return
    # Se já existe qualquer usuário, o bootstrap já foi concluído.
    if db.query(Usuario).count() > 0:
        return
    dados = UsuarioCreate(
        nome_completo=settings.first_admin_nome,
        email=settings.first_admin_email,
        senha=settings.first_admin_password,
        perfil="ADMIN",
    )
    usuario_service.criar_usuario(db, dados)
