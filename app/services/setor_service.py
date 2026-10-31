from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.model.setor import Setor
from app.schemas.setor_schema import SetorCreate
from app.services.common_service import montar_pagina, paginar


def obter_setor_por_id(db: Session, setor_id: int) -> Setor | None:
    return db.get(Setor, setor_id)


def obter_setor_por_nome(db: Session, nome: str) -> Setor | None:
    return db.query(Setor).filter(Setor.nome == nome).first()


def listar_setores(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    busca: str | None = None,
    status_setor: str | None = None,
):
    query = db.query(Setor)
    if busca:
        termo = f"%{busca}%"
        query = query.filter(Setor.nome.ilike(termo) | Setor.descricao.ilike(termo))
    if status_setor:
        query = query.filter(Setor.status == status_setor)

    query = query.order_by(Setor.nome)
    items, total = paginar(query, skip, limit)
    return montar_pagina(items, total, skip, limit)


def criar_setor(db: Session, setor: SetorCreate) -> Setor:
    if obter_setor_por_nome(db, setor.nome):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Já existe um setor cadastrado com este nome",
        )
    db_setor = Setor(nome=setor.nome, descricao=setor.descricao)
    db.add(db_setor)
    db.commit()
    db.refresh(db_setor)
    return db_setor


def atualizar_setor(db: Session, db_setor: Setor, dados: dict) -> Setor:
    novo_nome = dados.get("nome")
    if novo_nome and novo_nome != db_setor.nome:
        existente = obter_setor_por_nome(db, novo_nome)
        if existente and existente.id != db_setor.id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Já existe um setor cadastrado com este nome",
            )

    for campo, valor in dados.items():
        setattr(db_setor, campo, valor)

    db.commit()
    db.refresh(db_setor)
    return db_setor


def deletar_setor(db: Session, db_setor: Setor) -> None:
    if db_setor.usuarios or db_setor.items_backlog:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Não é possível excluir um setor com usuários ou itens de backlog vinculados",
        )
    db.delete(db_setor)
    db.commit()
