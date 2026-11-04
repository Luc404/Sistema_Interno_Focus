"""Serviço de tarefas pessoais.

Implementa listagem por usuário com busca/filtro e ordenação por prazo, CRUD
básico e mudança de status limitada aos valores permitidos.
"""

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.model.agenda import TarefaPessoal
from app.schemas.tarefa_pessoal_schema import TarefaPessoalCreate
from app.services.common_service import montar_pagina, paginar


def obter_tarefa_por_id(db: Session, tarefa_id: int) -> TarefaPessoal | None:
    """Busca uma tarefa pessoal pelo ID.

    Args:
        db: Sessão do SQLAlchemy.
        tarefa_id: Identificador primário da tarefa.

    Returns:
        A tarefa encontrada ou ``None``.

    Raises:
        Nenhuma exceção de negócio; erros de banco são propagados.
    """
    return db.get(TarefaPessoal, tarefa_id)


def listar_tarefas_por_usuario(
    db: Session,
    usuario_id: int,
    skip: int = 0,
    limit: int = 100,
    busca: str | None = None,
    status_tarefa: str | None = None,
):
    """Lista as tarefas de um usuário com busca, filtro e ordenação por prazo.

    Args:
        db: Sessão do SQLAlchemy.
        usuario_id: ID do usuário dono das tarefas.
        skip: Offset da paginação.
        limit: Máximo de tarefas retornadas.
        busca: Texto parcial pesquisado em título e descrição.
        status_tarefa: Status exato da tarefa.

    Returns:
        Um objeto ``Page`` com as tarefas e o total filtrado.

    Raises:
        Nenhuma exceção de negócio; erros de banco são propagados.
    """
    # Sempre restringe às tarefas do usuário informado.
    query = db.query(TarefaPessoal).filter(TarefaPessoal.usuario_id == usuario_id)
    if busca:
        termo = f"%{busca}%"
        # Pesquisa no título OU na descrição.
        query = query.filter(
            TarefaPessoal.titulo.ilike(termo) | TarefaPessoal.descricao.ilike(termo)
        )
    if status_tarefa:
        query = query.filter(TarefaPessoal.status == status_tarefa)

    # Ordena primeiro as tarefas com prazo (data_limite nula vai para o fim)
    # e, dentro das com prazo, pela data crescente.
    query = query.order_by(TarefaPessoal.data_limite.is_(None), TarefaPessoal.data_limite)
    items, total = paginar(query, skip, limit)
    return montar_pagina(items, total, skip, limit)


def criar_tarefa(db: Session, tarefa: TarefaPessoalCreate, usuario_id: int) -> TarefaPessoal:
    """Cria uma nova tarefa pessoal para o usuário informado.

    Args:
        db: Sessão do SQLAlchemy.
        tarefa: Dados de criação da tarefa.
        usuario_id: ID do usuário dono da tarefa.

    Returns:
        A tarefa persistida e recarregada do banco.

    Raises:
        Erros de banco são propagados.
    """
    db_tarefa = TarefaPessoal(
        titulo=tarefa.titulo,
        descricao=tarefa.descricao,
        data_limite=tarefa.data_limite,
        status=tarefa.status,
        usuario_id=usuario_id,
    )
    db.add(db_tarefa)
    db.commit()
    db.refresh(db_tarefa)
    return db_tarefa


def atualizar_tarefa(db: Session, db_tarefa: TarefaPessoal, dados: dict) -> TarefaPessoal:
    """Atualiza parcialmente uma tarefa pessoal.

    Args:
        db: Sessão do SQLAlchemy.
        db_tarefa: Tarefa já carregada que será modificada.
        dados: Campos a alterar.

    Returns:
        A tarefa atualizada e recarregada do banco.

    Raises:
        Erros de banco são propagados.
    """
    # Aplica dinamicamente os campos recebidos.
    for campo, valor in dados.items():
        setattr(db_tarefa, campo, valor)
    db.commit()
    db.refresh(db_tarefa)
    return db_tarefa


def mudar_status(db: Session, db_tarefa: TarefaPessoal, novo_status: str) -> TarefaPessoal:
    """Valida e aplica um novo status à tarefa.

    Args:
        db: Sessão do SQLAlchemy.
        db_tarefa: Tarefa que terá o status alterado.
        novo_status: Status desejado.

    Returns:
        A tarefa com o novo status persistido.

    Raises:
        HTTPException: 400 quando o status não está entre os permitidos.
    """
    # Conjunto fechado de status válidos para tarefas pessoais.
    if novo_status not in {"PENDENTE", "EM_ANDAMENTO", "CONCLUIDA"}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Status inválido",
        )
    db_tarefa.status = novo_status
    db.commit()
    db.refresh(db_tarefa)
    return db_tarefa


def deletar_tarefa(db: Session, db_tarefa: TarefaPessoal) -> None:
    """Remove uma tarefa pessoal do banco.

    Args:
        db: Sessão do SQLAlchemy.
        db_tarefa: Tarefa a ser removida.

    Returns:
        ``None``.

    Raises:
        Erros de banco são propagados.
    """
    db.delete(db_tarefa)
    db.commit()
