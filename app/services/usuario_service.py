from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password
from app.core.validators import validar_setor
from app.model.usuario import Usuario
from app.schemas.usuario_schema import UsuarioCreate
from app.services.common_service import montar_pagina, paginar


def obter_usuario_por_email(db: Session, email: str) -> Usuario | None:
    return db.query(Usuario).filter(Usuario.email == email).first()


def obter_usuario_por_id(db: Session, usuario_id: int) -> Usuario | None:
    return db.get(Usuario, usuario_id)


def listar_usuarios(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    busca: str | None = None,
    ativo: bool | None = None,
    setor_id: int | None = None,
):
    query = db.query(Usuario)
    if busca:
        termo = f"%{busca}%"
        query = query.filter(
            Usuario.nome_completo.ilike(termo) | Usuario.email.ilike(termo)
        )
    if ativo is not None:
        query = query.filter(Usuario.ativo == ativo)
    if setor_id is not None:
        query = query.filter(Usuario.setor_id == setor_id)

    query = query.order_by(Usuario.nome_completo)
    items, total = paginar(query, skip, limit)
    return montar_pagina(items, total, skip, limit)


def criar_usuario(db: Session, usuario: UsuarioCreate) -> Usuario:
    if obter_usuario_por_email(db, usuario.email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Já existe um usuário cadastrado com este e-mail",
        )
    validar_setor(db, usuario.setor_id)

    db_usuario = Usuario(
        nome_completo=usuario.nome_completo,
        email=usuario.email,
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
    if "email" in dados and dados["email"] and dados["email"] != db_usuario.email:
        if obter_usuario_por_email(db, dados["email"]):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Já existe um usuário cadastrado com este e-mail",
            )
    if "setor_id" in dados:
        validar_setor(db, dados["setor_id"])

    for campo, valor in dados.items():
        setattr(db_usuario, campo, valor)

    db.commit()
    db.refresh(db_usuario)
    return db_usuario


def desativar_usuario(db: Session, db_usuario: Usuario) -> Usuario:
    db_usuario.ativo = False
    db.commit()
    db.refresh(db_usuario)
    return db_usuario


def reativar_usuario(db: Session, db_usuario: Usuario) -> Usuario:
    db_usuario.ativo = True
    db.commit()
    db.refresh(db_usuario)
    return db_usuario


def autenticar(db: Session, email: str, senha: str) -> Usuario | None:
    usuario = obter_usuario_por_email(db, email)
    if not usuario or not verify_password(senha, usuario.senha_hash):
        return None
    return usuario


def alterar_senha(db: Session, db_usuario: Usuario, senha_atual: str, nova_senha: str) -> None:
    if not verify_password(senha_atual, db_usuario.senha_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Senha atual incorreta",
        )
    db_usuario.senha_hash = hash_password(nova_senha)
    db.commit()
