"""Serviço de usuários.

Responsável pelo CRUD de usuários, validação de e-mail único e setor, hash de
senha no cadastro, ativação/desativação, autenticação por senha e alteração de
senha com verificação da senha atual.
"""

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password
from app.core.validators import validar_setor
from app.model.usuario import Usuario
from app.schemas.usuario_schema import UsuarioCreate
from app.services.common_service import montar_pagina, paginar


def obter_usuario_por_email(db: Session, email: str) -> Usuario | None:
    """Busca um usuário pelo e-mail exato.

    Args:
        db: Sessão do SQLAlchemy.
        email: E-mail a ser procurado.

    Returns:
        O usuário encontrado ou ``None``.

    Raises:
        Nenhuma exceção de negócio; erros de banco são propagados.
    """
    return db.query(Usuario).filter(Usuario.email == email).first()


def obter_usuario_por_id(db: Session, usuario_id: int) -> Usuario | None:
    """Busca um usuário pelo ID.

    Args:
        db: Sessão do SQLAlchemy.
        usuario_id: Identificador primário do usuário.

    Returns:
        O usuário encontrado ou ``None``.

    Raises:
        Nenhuma exceção de negócio; erros de banco são propagados.
    """
    return db.get(Usuario, usuario_id)


def listar_usuarios(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    busca: str | None = None,
    ativo: bool | None = None,
    setor_id: int | None = None,
):
    """Lista usuários com busca textual, filtros de ativação/setor e paginação.

    Args:
        db: Sessão do SQLAlchemy.
        skip: Offset da paginação.
        limit: Máximo de usuários retornados.
        busca: Texto parcial pesquisado em nome completo e e-mail.
        ativo: Quando informado, filtra por ativos/inativos.
        setor_id: ID do setor vinculado.

    Returns:
        Um objeto ``Page`` com os usuários e o total filtrado.

    Raises:
        Nenhuma exceção de negócio; erros de banco são propagados.
    """
    query = db.query(Usuario)
    if busca:
        termo = f"%{busca}%"
        # Pesquisa no nome completo OU no e-mail.
        query = query.filter(
            Usuario.nome_completo.ilike(termo) | Usuario.email.ilike(termo)
        )
    if ativo is not None:
        query = query.filter(Usuario.ativo == ativo)
    if setor_id is not None:
        query = query.filter(Usuario.setor_id == setor_id)

    # Ordena alfabeticamente pelo nome completo.
    query = query.order_by(Usuario.nome_completo)
    items, total = paginar(query, skip, limit)
    return montar_pagina(items, total, skip, limit)


def criar_usuario(db: Session, usuario: UsuarioCreate) -> Usuario:
    """Cria um novo usuário com senha armazenada em hash.

    Args:
        db: Sessão do SQLAlchemy.
        usuario: Dados de criação do usuário (inclui senha em texto plano).

    Returns:
        O usuário persistido e recarregado do banco.

    Raises:
        HTTPException: 409 quando o e-mail já está cadastrado e 404 quando o
            setor informado não existe (via validador).
    """
    # Garante unicidade do e-mail antes de inserir.
    if obter_usuario_por_email(db, usuario.email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Já existe um usuário cadastrado com este e-mail",
        )
    # Valida a existência do setor, quando informado.
    validar_setor(db, usuario.setor_id)

    db_usuario = Usuario(
        nome_completo=usuario.nome_completo,
        email=usuario.email,
        # Nunca persiste a senha em texto plano: aplica hash antes de salvar.
        senha_hash=hash_password(usuario.senha),
        cargo=usuario.cargo,
        perfil=usuario.perfil,
        setor_id=usuario.setor_id,
    )
    db.add(db_usuario)
    db.commit()
    db.refresh(db_usuario)
    return db_usuario


def atualizar_usuario(db: Session, db_usuario: Usuario, dados: dict) -> Usuario:
    """Atualiza parcialmente um usuário, validando e-mail e setor.

    Args:
        db: Sessão do SQLAlchemy.
        db_usuario: Usuário já carregado que será modificado.
        dados: Campos a alterar.

    Returns:
        O usuário atualizado e recarregado do banco.

    Raises:
        HTTPException: 409 quando o novo e-mail já pertence a outro usuário e
            404 quando o setor informado não existe.
    """
    # Só checa unicidade se o e-mail foi enviado e difere do atual.
    if "email" in dados and dados["email"] and dados["email"] != db_usuario.email:
        if obter_usuario_por_email(db, dados["email"]):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Já existe um usuário cadastrado com este e-mail",
            )
    # Se o setor foi informado, valida sua existência.
    if "setor_id" in dados:
        validar_setor(db, dados["setor_id"])

    # Aplica os campos recebidos dinamicamente.
    for campo, valor in dados.items():
        setattr(db_usuario, campo, valor)

    db.commit()
    db.refresh(db_usuario)
    return db_usuario


def desativar_usuario(db: Session, db_usuario: Usuario) -> Usuario:
    """Desativa logicamente um usuário (soft delete).

    Args:
        db: Sessão do SQLAlchemy.
        db_usuario: Usuário a ser desativado.

    Returns:
        O usuário atualizado e recarregado do banco.

    Raises:
        Erros de banco são propagados.
    """
    # Mantém o registro no banco, apenas marcando como inativo.
    db_usuario.ativo = False
    db.commit()
    db.refresh(db_usuario)
    return db_usuario


def reativar_usuario(db: Session, db_usuario: Usuario) -> Usuario:
    """Reativa um usuário previamente desativado.

    Args:
        db: Sessão do SQLAlchemy.
        db_usuario: Usuário a ser reativado.

    Returns:
        O usuário atualizado e recarregado do banco.

    Raises:
        Erros de banco são propagados.
    """
    db_usuario.ativo = True
    db.commit()
    db.refresh(db_usuario)
    return db_usuario


def autenticar(db: Session, email: str, senha: str) -> Usuario | None:
    """Valida as credenciais de um usuário.

    Args:
        db: Sessão do SQLAlchemy.
        email: E-mail informado.
        senha: Senha em texto plano informada.

    Returns:
        O usuário autenticado ou ``None`` quando o e-mail não existe ou a senha
        não corresponde ao hash armazenado.

    Raises:
        Nenhuma exceção de negócio; erros de banco são propagados.
    """
    usuario = obter_usuario_por_email(db, email)
    # verify_password compara a senha em texto plano com o hash salvo.
    if not usuario or not verify_password(senha, usuario.senha_hash):
        return None
    return usuario


def alterar_senha(db: Session, db_usuario: Usuario, senha_atual: str, nova_senha: str) -> None:
    """Altera a senha de um usuário após verificar a senha atual.

    Args:
        db: Sessão do SQLAlchemy.
        db_usuario: Usuário que terá a senha alterada.
        senha_atual: Senha atual em texto plano para confirmação.
        nova_senha: Nova senha em texto plano.

    Returns:
        ``None``.

    Raises:
        HTTPException: 400 quando a senha atual está incorreta.
    """
    # Confirma a identidade verificando a senha atual contra o hash.
    if not verify_password(senha_atual, db_usuario.senha_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Senha atual incorreta",
        )
    # Gera e persiste o hash da nova senha.
    db_usuario.senha_hash = hash_password(nova_senha)
    db.commit()
