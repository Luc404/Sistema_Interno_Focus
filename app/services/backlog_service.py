"""Serviço de itens de backlog.

Implementa listagem filtrada/paginada, criação, atualização, mudança de status
(com validação da máquina de estados) e exclusão de itens de backlog.
"""

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.validators import validar_setor
from app.model.backlog import ItemBacklog
from app.schemas.backlog_schema import BacklogCreate
from app.services.common_service import montar_pagina, paginar

# Máquina de estados simples: mapeia o status atual para os status permitidos.
# Observação: nesta configuração todas as transições são permitidas.
TRANSICOES_STATUS = {
    "PENDENTE": {"PENDENTE", "EM_ANDAMENTO", "CONCLUIDO"},
    "EM_ANDAMENTO": {"PENDENTE", "EM_ANDAMENTO", "CONCLUIDO"},
    "CONCLUIDO": {"PENDENTE", "EM_ANDAMENTO", "CONCLUIDO"},
}


def obter_item_por_id(db: Session, item_id: int) -> ItemBacklog | None:
    """Busca um item de backlog pelo ID.

    Args:
        db: Sessão do SQLAlchemy.
        item_id: Identificador primário do item.

    Returns:
        O item encontrado ou ``None`` se não existir.

    Raises:
        Nenhuma exceção de negócio; erros de banco são propagados.
    """
    # Busca direta pela chave primária.
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
    """Lista itens de backlog com filtros combináveis e paginação.

    Args:
        db: Sessão do SQLAlchemy.
        skip: Offset da paginação.
        limit: Máximo de itens retornados.
        busca: Texto parcial pesquisado em título e descrição.
        status_item: Status exato do item.
        tipo: Tipo exato do item.
        prioridade: Prioridade exata do item.
        setor_id: ID do setor vinculado.
        autor_id: ID do autor do item.

    Returns:
        Um objeto ``Page`` com os itens e o total filtrado.

    Raises:
        Nenhuma exceção de negócio; erros de banco são propagados.
    """
    query = db.query(ItemBacklog)
    if busca:
        termo = f"%{busca}%"
        # O operador ``|`` representa OR: casa no título OU na descrição.
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

    # Itens mais recentes primeiro.
    query = query.order_by(ItemBacklog.data_criacao.desc())
    items, total = paginar(query, skip, limit)
    return montar_pagina(items, total, skip, limit)


def criar_item(db: Session, item: BacklogCreate, autor_id: int) -> ItemBacklog:
    """Cria um novo item de backlog.

    Args:
        db: Sessão do SQLAlchemy.
        item: Dados de criação do item.
        autor_id: ID do usuário autor do item.

    Returns:
        O item persistido e recarregado do banco.

    Raises:
        HTTPException: 404 quando o setor informado não existe (via validador).
    """
    # Garante que o setor referenciado exista antes de criar o item.
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
    """Atualiza parcialmente um item de backlog.

    Args:
        db: Sessão do SQLAlchemy.
        db_item: Item já carregado que será modificado.
        dados: Campos a alterar.

    Returns:
        O item atualizado e recarregado do banco.

    Raises:
        HTTPException: 404 quando o novo setor informado não existe.
    """
    # Se o setor está sendo alterado, valida a existência do novo setor.
    if "setor_id" in dados:
        validar_setor(db, dados["setor_id"])
    # Aplica dinamicamente os campos recebidos.
    for campo, valor in dados.items():
        setattr(db_item, campo, valor)
    db.commit()
    db.refresh(db_item)
    return db_item


def mudar_status(db: Session, db_item: ItemBacklog, novo_status: str) -> ItemBacklog:
    """Valida e aplica uma transição de status do item.

    Args:
        db: Sessão do SQLAlchemy.
        db_item: Item que terá o status alterado.
        novo_status: Status desejado.

    Returns:
        O item com o novo status persistido.

    Raises:
        HTTPException: 400 quando a transição não é permitida pela máquina de
            estados (ou quando o status atual é desconhecido).
    """
    # Consulta o conjunto de status permitidos a partir do status atual.
    # ``.get(..., set())`` evita KeyError para status inesperados.
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
    """Remove um item de backlog do banco.

    Args:
        db: Sessão do SQLAlchemy.
        db_item: Item a ser removido.

    Returns:
        ``None``.

    Raises:
        Erros de banco/integridade são propagados.
    """
    db.delete(db_item)
    db.commit()
