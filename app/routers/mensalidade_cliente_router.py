from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, require_perfis
from app.database import get_db
from app.model.usuario import Usuario
from app.schemas.common import Mensagem, Page
from app.schemas.mensalidade_cliente_schema import (
    MensalidadeClienteCreate,
    MensalidadeClienteResponse,
    MensalidadeClienteUpdate,
    MensalidadePagarRequest,
    MensalidadeResumo,
)
from app.services import mensalidade_cliente_service

router = APIRouter(prefix="/api/mensalidades", tags=["Agenda - Mensalidades dos Clientes"])


@router.post("/", response_model=MensalidadeClienteResponse, status_code=status.HTTP_201_CREATED)
def criar_mensalidade(
    mensalidade: MensalidadeClienteCreate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_perfis("ADMIN")),
):
    return mensalidade_cliente_service.criar_mensalidade(db=db, mensalidade=mensalidade)


@router.get("/", response_model=Page[MensalidadeClienteResponse])
def listar_mensalidades(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    busca: str | None = None,
    status_pagamento: str | None = None,
    vencimento_inicio: datetime | None = None,
    vencimento_fim: datetime | None = None,
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    return mensalidade_cliente_service.listar_mensalidades(
        db=db,
        skip=skip,
        limit=limit,
        busca=busca,
        status_pagamento=status_pagamento,
        vencimento_inicio=vencimento_inicio,
        vencimento_fim=vencimento_fim,
    )


@router.get("/resumo", response_model=MensalidadeResumo)
def obter_resumo(
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    return mensalidade_cliente_service.resumo(db)


@router.get("/{mensalidade_id}", response_model=MensalidadeClienteResponse)
def obter_mensalidade(
    mensalidade_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    db_mensalidade = mensalidade_cliente_service.obter_mensalidade_por_id(
        db=db, mensalidade_id=mensalidade_id
    )
    if not db_mensalidade:
        raise HTTPException(status_code=404, detail="Mensalidade não encontrada")
    return db_mensalidade


@router.patch("/{mensalidade_id}", response_model=MensalidadeClienteResponse)
def atualizar_mensalidade(
    mensalidade_id: int,
    dados: MensalidadeClienteUpdate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_perfis("ADMIN")),
):
    db_mensalidade = mensalidade_cliente_service.obter_mensalidade_por_id(
        db=db, mensalidade_id=mensalidade_id
    )
    if not db_mensalidade:
        raise HTTPException(status_code=404, detail="Mensalidade não encontrada")
    return mensalidade_cliente_service.atualizar_mensalidade(
        db, db_mensalidade, dados.model_dump(exclude_unset=True)
    )


@router.patch("/{mensalidade_id}/pagar", response_model=MensalidadeClienteResponse)
def pagar_mensalidade(
    mensalidade_id: int,
    dados: MensalidadePagarRequest,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_perfis("ADMIN")),
):
    db_mensalidade = mensalidade_cliente_service.obter_mensalidade_por_id(
        db=db, mensalidade_id=mensalidade_id
    )
    if not db_mensalidade:
        raise HTTPException(status_code=404, detail="Mensalidade não encontrada")
    return mensalidade_cliente_service.pagar_mensalidade(db, db_mensalidade, dados)


@router.delete("/{mensalidade_id}", response_model=Mensagem)
def deletar_mensalidade(
    mensalidade_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_perfis("ADMIN")),
):
    db_mensalidade = mensalidade_cliente_service.obter_mensalidade_por_id(
        db=db, mensalidade_id=mensalidade_id
    )
    if not db_mensalidade:
        raise HTTPException(status_code=404, detail="Mensalidade não encontrada")
    mensalidade_cliente_service.deletar_mensalidade(db, db_mensalidade)
    return Mensagem(mensagem="Mensalidade excluída com sucesso")
