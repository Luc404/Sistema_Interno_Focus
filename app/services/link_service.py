"""Serviço de links da biblioteca.

Implementa listagem filtrada/paginada e CRUD de links, convertendo a URL para
string ao persistir/atualizar e atribuindo o usuário dono no cadastro.
"""

from sqlalchemy.orm import Session

from app.model.biblioteca import Link
from app.schemas.link_schema import LinkCreate
from app.services.common_service import montar_pagina, paginar


def obter_link_por_id(db: Session, link_id: int) -> Link | None:
    """Busca um link pelo ID.

    Args:
        db: Sessão do SQLAlchemy.
        link_id: Identificador primário do link.

    Returns:
        O link encontrado ou ``None``.

    Raises:
        Nenhuma exceção de negócio; erros de banco são propagados.
    """
    return db.get(Link, link_id)


def listar_links(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    busca: str | None = None,
    categoria: str | None = None,
    usuario_id: int | None = None,
):
    """Lista links com busca, filtros de categoria/usuário e paginação.

    Args:
        db: Sessão do SQLAlchemy.
        skip: Offset da paginação.
        limit: Máximo de links retornados.
        busca: Texto parcial pesquisado em título e descrição.
        categoria: Nome exato da categoria do link.
        usuario_id: ID do usuário dono do link.

    Returns:
        Um objeto ``Page`` com os links e o total filtrado.

    Raises:
        Nenhuma exceção de negócio; erros de banco são propagados.
    """
    query = db.query(Link)
    if busca:
        termo = f"%{busca}%"
        # Casa o termo no título OU na descrição.
        query = query.filter(Link.titulo.ilike(termo) | Link.descricao.ilike(termo))
    if categoria:
        query = query.filter(Link.categoria == categoria)
    if usuario_id is not None:
        query = query.filter(Link.usuario_id == usuario_id)

    # Links mais recentes primeiro.
    query = query.order_by(Link.data_criacao.desc())
    items, total = paginar(query, skip, limit)
    return montar_pagina(items, total, skip, limit)


def criar_link(db: Session, link: LinkCreate, usuario_id: int) -> Link:
    """Cadastra um novo link para o usuário informado.

    Args:
        db: Sessão do SQLAlchemy.
        link: Dados de criação do link.
        usuario_id: ID do usuário dono do link.

    Returns:
        O link persistido e recarregado do banco.

    Raises:
        Erros de banco são propagados.
    """
    db_link = Link(
        titulo=link.titulo,
        # Converte o tipo URL (ex.: Pydantic AnyUrl) para string simples.
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
    """Atualiza parcialmente um link.

    Args:
        db: Sessão do SQLAlchemy.
        db_link: Link já carregado que será modificado.
        dados: Campos a alterar.

    Returns:
        O link atualizado e recarregado do banco.

    Raises:
        Erros de banco são propagados.
    """
    # Se a URL veio no payload e não é nula, normaliza para string.
    if "url" in dados and dados["url"] is not None:
        dados["url"] = str(dados["url"])
    for campo, valor in dados.items():
        setattr(db_link, campo, valor)
    db.commit()
    db.refresh(db_link)
    return db_link


def deletar_link(db: Session, db_link: Link) -> None:
    """Remove um link do banco.

    Args:
        db: Sessão do SQLAlchemy.
        db_link: Link a ser removido.

    Returns:
        ``None``.

    Raises:
        Erros de banco são propagados.
    """
    db.delete(db_link)
    db.commit()
