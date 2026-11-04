"""Serviço de setores.

Implementa busca por ID/nome, listagem filtrada e paginada e CRUD de setores,
garantindo unicidade de nome e bloqueio de exclusão quando há usuários ou
itens de backlog vinculados.
"""

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.model.setor import Setor
from app.schemas.setor_schema import SetorCreate
from app.services.common_service import montar_pagina, paginar


def obter_setor_por_id(db: Session, setor_id: int) -> Setor | None:
    """Busca um setor pelo ID.

    Args:
        db: Sessão do SQLAlchemy.
        setor_id: Identificador primário do setor.

    Returns:
        O setor encontrado ou ``None``.

    Raises:
        Nenhuma exceção de negócio; erros de banco são propagados.
    """
    return db.get(Setor, setor_id)


def obter_setor_por_nome(db: Session, nome: str) -> Setor | None:
    """Busca um setor pelo nome exato.

    Args:
        db: Sessão do SQLAlchemy.
        nome: Nome do setor.

    Returns:
        O setor encontrado ou ``None``.

    Raises:
        Nenhuma exceção de negócio; erros de banco são propagados.
    """
    return db.query(Setor).filter(Setor.nome == nome).first()


def listar_setores(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    busca: str | None = None,
    status_setor: str | None = None,
):
    """Lista setores com busca textual, filtro de status e paginação.

    Args:
        db: Sessão do SQLAlchemy.
        skip: Offset da paginação.
        limit: Máximo de setores retornados.
        busca: Texto parcial pesquisado em nome e descrição.
        status_setor: Status exato do setor.

    Returns:
        Um objeto ``Page`` com os setores e o total filtrado.

    Raises:
        Nenhuma exceção de negócio; erros de banco são propagados.
    """
    query = db.query(Setor)
    if busca:
        termo = f"%{busca}%"
        # Pesquisa no nome OU na descrição.
        query = query.filter(Setor.nome.ilike(termo) | Setor.descricao.ilike(termo))
    if status_setor:
        query = query.filter(Setor.status == status_setor)

    # Ordena alfabeticamente pelo nome.
    query = query.order_by(Setor.nome)
    items, total = paginar(query, skip, limit)
    return montar_pagina(items, total, skip, limit)


def criar_setor(db: Session, setor: SetorCreate) -> Setor:
    """Cria um novo setor garantindo nome único.

    Args:
        db: Sessão do SQLAlchemy.
        setor: Dados de criação do setor.

    Returns:
        O setor persistido e recarregado do banco.

    Raises:
        HTTPException: 409 quando já existe um setor com o mesmo nome.
    """
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
    """Atualiza parcialmente um setor, validando unicidade do nome.

    Args:
        db: Sessão do SQLAlchemy.
        db_setor: Setor já carregado que será modificado.
        dados: Campos a alterar.

    Returns:
        O setor atualizado e recarregado do banco.

    Raises:
        HTTPException: 409 quando o novo nome já pertence a outro setor.
    """
    novo_nome = dados.get("nome")
    # Só valida unicidade quando o nome foi enviado e realmente mudou.
    if novo_nome and novo_nome != db_setor.nome:
        existente = obter_setor_por_nome(db, novo_nome)
        # Ignora o próprio setor ao verificar conflito.
        if existente and existente.id != db_setor.id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Já existe um setor cadastrado com este nome",
            )

    # Aplica os campos recebidos dinamicamente.
    for campo, valor in dados.items():
        setattr(db_setor, campo, valor)

    db.commit()
    db.refresh(db_setor)
    return db_setor


def deletar_setor(db: Session, db_setor: Setor) -> None:
    """Exclui um setor se não houver vínculos com usuários ou backlog.

    Args:
        db: Sessão do SQLAlchemy.
        db_setor: Setor a ser removido.

    Returns:
        ``None``.

    Raises:
        HTTPException: 409 quando existem usuários ou itens de backlog
            vinculados ao setor.
    """
    # Protege vínculos antes de remover o setor.
    if db_setor.usuarios or db_setor.items_backlog:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Não é possível excluir um setor com usuários ou itens de backlog vinculados",
        )
    db.delete(db_setor)
    db.commit()
