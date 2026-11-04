"""Serviço de mensalidades de clientes.

Responsável pelo CRUD de mensalidades, pela listagem filtrada por período e
status, pelo registro de pagamento (com regra de não pagar duas vezes) e pela
consolidação do resumo financeiro (contagens e valores pendentes/recebidos).
"""

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
    """Busca uma mensalidade pelo ID.

    Args:
        db: Sessão do SQLAlchemy.
        mensalidade_id: Identificador primário da mensalidade.

    Returns:
        A mensalidade encontrada ou ``None``.

    Raises:
        Nenhuma exceção de negócio; erros de banco são propagados.
    """
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
    """Lista mensalidades com filtros de cliente, status e período de vencimento.

    Args:
        db: Sessão do SQLAlchemy.
        skip: Offset da paginação.
        limit: Máximo de mensalidades retornadas.
        busca: Texto parcial pesquisado no nome do cliente.
        status_pagamento: Status exato do pagamento.
        vencimento_inicio: Limite inferior (inclusivo) de vencimento.
        vencimento_fim: Limite superior (inclusivo) de vencimento.

    Returns:
        Um objeto ``Page`` com as mensalidades e o total filtrado.

    Raises:
        Nenhuma exceção de negócio; erros de banco são propagados.
    """
    query = db.query(MensalidadeCliente)
    if busca:
        # Pesquisa parcial e case-insensitive pelo nome do cliente.
        query = query.filter(MensalidadeCliente.nome_cliente.ilike(f"%{busca}%"))
    if status_pagamento:
        query = query.filter(MensalidadeCliente.status_pagamento == status_pagamento)
    if vencimento_inicio:
        query = query.filter(MensalidadeCliente.data_vencimento >= vencimento_inicio)
    if vencimento_fim:
        query = query.filter(MensalidadeCliente.data_vencimento <= vencimento_fim)

    # Ordena pela data de vencimento (mais próximas primeiro).
    query = query.order_by(MensalidadeCliente.data_vencimento)
    items, total = paginar(query, skip, limit)
    return montar_pagina(items, total, skip, limit)


def criar_mensalidade(
    db: Session,
    mensalidade: MensalidadeClienteCreate,
) -> MensalidadeCliente:
    """Cria uma nova mensalidade de cliente.

    Args:
        db: Sessão do SQLAlchemy.
        mensalidade: Dados de criação da mensalidade.

    Returns:
        A mensalidade persistida e recarregada do banco.

    Raises:
        Erros de banco são propagados.
    """
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
    """Atualiza parcialmente uma mensalidade.

    Args:
        db: Sessão do SQLAlchemy.
        db_mensalidade: Mensalidade já carregada que será modificada.
        dados: Campos a alterar.

    Returns:
        A mensalidade atualizada e recarregada do banco.

    Raises:
        Erros de banco são propagados.
    """
    # Aplica dinamicamente os campos recebidos no objeto ORM.
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
    """Registra o pagamento de uma mensalidade ainda não paga.

    Args:
        db: Sessão do SQLAlchemy.
        db_mensalidade: Mensalidade a ser marcada como paga.
        dados: Dados do pagamento (data opcional e observação opcional).

    Returns:
        A mensalidade atualizada e recarregada do banco.

    Raises:
        HTTPException: 409 quando a mensalidade já está com status ``PAGO``.
    """
    # Impede pagamento duplicado da mesma mensalidade.
    if db_mensalidade.status_pagamento == "PAGO":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Esta mensalidade já foi paga",
        )
    db_mensalidade.status_pagamento = "PAGO"
    # Usa a data informada ou a data/hora atual em UTC como fallback.
    db_mensalidade.data_pagamento = dados.data_pagamento or datetime.now(timezone.utc)
    # A observação só é sobrescrita quando explicitamente enviada.
    if dados.observacao is not None:
        db_mensalidade.observacao = dados.observacao
    db.commit()
    db.refresh(db_mensalidade)
    return db_mensalidade


def deletar_mensalidade(db: Session, db_mensalidade: MensalidadeCliente) -> None:
    """Remove uma mensalidade do banco.

    Args:
        db: Sessão do SQLAlchemy.
        db_mensalidade: Mensalidade a ser removida.

    Returns:
        ``None``.

    Raises:
        Erros de banco são propagados.
    """
    db.delete(db_mensalidade)
    db.commit()


def resumo(db: Session) -> MensalidadeResumo:
    """Consolida contagens e valores financeiros das mensalidades.

    Args:
        db: Sessão do SQLAlchemy.

    Returns:
        Um ``MensalidadeResumo`` com totais por status e somatórios de valores
        pendentes e recebidos.

    Raises:
        Nenhuma exceção de negócio; erros de banco são propagados.
    """
    # Total geral de mensalidades.
    total = db.query(func.count(MensalidadeCliente.id)).scalar() or 0
    # Contagens por status de pagamento.
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
    # Soma dos valores em aberto (pendentes + atrasados). coalesce evita NULL.
    valor_pendente = (
        db.query(func.coalesce(func.sum(MensalidadeCliente.valor), 0))
        .filter(MensalidadeCliente.status_pagamento.in_(["PENDENTE", "ATRASADO"]))
        .scalar()
        or Decimal("0")
    )
    # Soma dos valores efetivamente pagos.
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
        # Decimal -> float para o schema de resposta.
        valor_total_pendente=float(valor_pendente),
        valor_total_recebido=float(valor_recebido),
    )
