from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.model.agenda import TarefaPessoal
from app.schemas.tarefa_pessoal_schema import TarefaPessoalCreate
from app.services.common_service import montar_pagina, paginar


def obter_tarefa_por_id(db: Session, tarefa_id: int) -> TarefaPessoal | None:
    return db.get(TarefaPessoal, tarefa_id)


def listar_tarefas_por_usuario(
    db: Session,
    usuario_id: int,
    skip: int = 0,
    limit: int = 100,
    busca: str | None = None,
    status_tarefa: str | None = None,
):
    query = db.query(TarefaPessoal).filter(TarefaPessoal.usuario_id == usuario_id)
    if busca:
        termo = f"%{busca}%"
        query = query.filter(
            TarefaPessoal.titulo.ilike(termo) | TarefaPessoal.descricao.ilike(termo)
        )
    if status_tarefa:
        query = query.filter(TarefaPessoal.status == status_tarefa)

    query = query.order_by(TarefaPessoal.data_limite.is_(None), TarefaPessoal.data_limite)
    items, total = paginar(query, skip, limit)
    return montar_pagina(items, total, skip, limit)


def criar_tarefa(db: Session, tarefa: TarefaPessoalCreate, usuario_id: int) -> TarefaPessoal:
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
    for campo, valor in dados.items():
        setattr(db_tarefa, campo, valor)
    db.commit()
    db.refresh(db_tarefa)
    return db_tarefa


def mudar_status(db: Session, db_tarefa: TarefaPessoal, novo_status: str) -> TarefaPessoal:
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
    db.delete(db_tarefa)
    db.commit()
