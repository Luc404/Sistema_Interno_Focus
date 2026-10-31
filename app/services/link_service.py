from sqlalchemy.orm import Session

from app.model.biblioteca import Link
from app.schemas.link_schema import LinkCreate
from app.services.common_service import montar_pagina, paginar


def obter_link_por_id(db: Session, link_id: int) -> Link | None:
    return db.get(Link, link_id)


def listar_links(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    busca: str | None = None,
    categoria: str | None = None,
    usuario_id: int | None = None,
):
    query = db.query(Link)
    if busca:
        termo = f"%{busca}%"
        query = query.filter(Link.titulo.ilike(termo) | Link.descricao.ilike(termo))
    if categoria:
        query = query.filter(Link.categoria == categoria)
    if usuario_id is not None:
        query = query.filter(Link.usuario_id == usuario_id)

    query = query.order_by(Link.data_criacao.desc())
    items, total = paginar(query, skip, limit)
    return montar_pagina(items, total, skip, limit)


def criar_link(db: Session, link: LinkCreate, usuario_id: int) -> Link:
    db_link = Link(
        titulo=link.titulo,
        url=str(link.url),
        descricao=link.descricao,
        categoria=link.categoria,
        usuario_id=usuario_id,
    )
    db.add(db_link)
    db.commit()
    db.refresh(db_link)
    return db_link


def atualizar_link(db: Session, db_link: Link, dados: dict) -> Link:
    if "url" in dados and dados["url"] is not None:
        dados["url"] = str(dados["url"])
    for campo, valor in dados.items():
        setattr(db_link, campo, valor)
    db.commit()
    db.refresh(db_link)
    return db_link


def deletar_link(db: Session, db_link: Link) -> None:
    db.delete(db_link)
    db.commit()
