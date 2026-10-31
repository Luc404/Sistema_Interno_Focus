from datetime import datetime, timezone
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.model.agenda import MensalidadeCliente
from app.schemas.mensalidade_cliente_schema import (
    MensalidadeClienteCreate,
    MensalidadePagarRequest,
    MensalidadeResumo,
)
from app.services.common_service import montar_pagina, paginar


def obter_mensalidade_por_id(db: Session, mensalidade_id: int) -> MensalidadeCliente | None:
    return db.get(MensalidadeCliente, mensalidade_id)


def listar_mensalidades(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    busca: str | None = None,
    status_pagamento: str | None = None,
    vencimento_inicio: datetime | None = None,
    vencimento_fim: datetime | None = None,
):
    query = db.query(MensalidadeCliente)
    if busca:
        query = query.filter(MensalidadeCliente.nome_cliente.ilike(f"%{busca}%"))
    if status_pagamento:
        query = query.filter(MensalidadeCliente.status_pagamento == status_pagamento)
    if vencimento_inicio:
        query = query.filter(MensalidadeCliente.data_vencimento >= vencimento_inicio)
    if vencimento_fim:
        query = query.filter(MensalidadeCliente.data_vencimento <= vencimento_fim)

    query = query.order_by(MensalidadeCliente.data_vencimento)
    items, total = paginar(query, skip, limit)
    return montar_pagina(items, total, skip, limit)


def criar_mensalidade(
    db: Session,
    mensalidade: MensalidadeClienteCreate,
) -> MensalidadeCliente:
    db_mensalidade = MensalidadeCliente(
        nome_cliente=mensalidade.nome_cliente,
        valor=mensalidade.valor,
        data_vencimento=mensalidade.data_vencimento,
        status_pagamento=mensalidade.status_pagamento,
        observacao=mensalidade.observacao,
    )
    db.add(db_mensalidade)
    db.commit()
    db.refresh(db_mensalidade)
    return db_mensalidade


def atualizar_mensalidade(
    db: Session,
    db_mensalidade: MensalidadeCliente,
    dados: dict,
) -> MensalidadeCliente:
    for campo, valor in dados.items():
        setattr(db_mensalidade, campo, valor)
    db.commit()
    db.refresh(db_mensalidade)
    return db_mensalidade


def pagar_mensalidade(
    db: Session,
    db_mensalidade: MensalidadeCliente,
    dados: MensalidadePagarRequest,
) -> MensalidadeCliente:
    if db_mensalidade.status_pagamento == "PAGO":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Esta mensalidade já foi paga",
        )
    db_mensalidade.status_pagamento = "PAGO"
    db_mensalidade.data_pagamento = dados.data_pagamento or datetime.now(timezone.utc)
    if dados.observacao is not None:
        db_mensalidade.observacao = dados.observacao
    db.commit()
    db.refresh(db_mensalidade)
    return db_mensalidade


def deletar_mensalidade(db: Session, db_mensalidade: MensalidadeCliente) -> None:
    db.delete(db_mensalidade)
    db.commit()


def resumo(db: Session) -> MensalidadeResumo:
    total = db.query(func.count(MensalidadeCliente.id)).scalar() or 0
    pendentes = (
        db.query(func.count(MensalidadeCliente.id))
        .filter(MensalidadeCliente.status_pagamento == "PENDENTE")
        .scalar()
        or 0
    )
    pagas = (
        db.query(func.count(MensalidadeCliente.id))
        .filter(MensalidadeCliente.status_pagamento == "PAGO")
        .scalar()
        or 0
    )
    atrasadas = (
        db.query(func.count(MensalidadeCliente.id))
        .filter(MensalidadeCliente.status_pagamento == "ATRASADO")
        .scalar()
        or 0
    )
    valor_pendente = (
        db.query(func.coalesce(func.sum(MensalidadeCliente.valor), 0))
        .filter(MensalidadeCliente.status_pagamento.in_(["PENDENTE", "ATRASADO"]))
        .scalar()
        or Decimal("0")
    )
    valor_recebido = (
        db.query(func.coalesce(func.sum(MensalidadeCliente.valor), 0))
        .filter(MensalidadeCliente.status_pagamento == "PAGO")
        .scalar()
        or Decimal("0")
    )
    return MensalidadeResumo(
        total=total,
        pendentes=pendentes,
        pagas=pagas,
        atrasadas=atrasadas,
        valor_total_pendente=float(valor_pendente),
        valor_total_recebido=float(valor_recebido),
    )
