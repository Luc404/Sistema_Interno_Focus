from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.validators import validar_setor
from app.model.backlog import ItemBacklog
from app.schemas.backlog_schema import BacklogCreate
from app.services.common_service import montar_pagina, paginar

TRANSICOES_STATUS = {
    "PENDENTE": {"PENDENTE", "EM_ANDAMENTO", "CONCLUIDO"},
    "EM_ANDAMENTO": {"PENDENTE", "EM_ANDAMENTO", "CONCLUIDO"},
    "CONCLUIDO": {"PENDENTE", "EM_ANDAMENTO", "CONCLUIDO"},
}


def obter_item_por_id(db: Session, item_id: int) -> ItemBacklog | None:
    return db.get(ItemBacklog, item_id)


def listar_itens(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    busca: str | None = None,
    status_item: str | None = None,
    tipo: str | None = None,
    prioridade: str | None = None,
    setor_id: int | None = None,
    autor_id: int | None = None,
):
    query = db.query(ItemBacklog)
    if busca:
        termo = f"%{busca}%"
        query = query.filter(
            ItemBacklog.titulo.ilike(termo) | ItemBacklog.descricao.ilike(termo)
        )
    if status_item:
        query = query.filter(ItemBacklog.status == status_item)
    if tipo:
        query = query.filter(ItemBacklog.tipo == tipo)
    if prioridade:
        query = query.filter(ItemBacklog.prioridade == prioridade)
    if setor_id is not None:
        query = query.filter(ItemBacklog.setor_id == setor_id)
    if autor_id is not None:
        query = query.filter(ItemBacklog.autor_id == autor_id)

    query = query.order_by(ItemBacklog.data_criacao.desc())
    items, total = paginar(query, skip, limit)
    return montar_pagina(items, total, skip, limit)


def criar_item(db: Session, item: BacklogCreate, autor_id: int) -> ItemBacklog:
    validar_setor(db, item.setor_id)
    db_item = ItemBacklog(
        titulo=item.titulo,
        descricao=item.descricao,
        tipo=item.tipo,
        prioridade=item.prioridade,
        status=item.status,
        setor_id=item.setor_id,
        autor_id=autor_id,
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


def atualizar_item(db: Session, db_item: ItemBacklog, dados: dict) -> ItemBacklog:
    if "setor_id" in dados:
        validar_setor(db, dados["setor_id"])
    for campo, valor in dados.items():
        setattr(db_item, campo, valor)
    db.commit()
    db.refresh(db_item)
    return db_item


def mudar_status(db: Session, db_item: ItemBacklog, novo_status: str) -> ItemBacklog:
    if novo_status not in TRANSICOES_STATUS.get(db_item.status, set()):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Transição de status inválida: {db_item.status} -> {novo_status}",
        )
    db_item.status = novo_status
    db.commit()
    db.refresh(db_item)
    return db_item


def deletar_item(db: Session, db_item: ItemBacklog) -> None:
    db.delete(db_item)
    db.commit()
