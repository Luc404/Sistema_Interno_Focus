from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.schemas.mensalidade_cliente_schema import MensalidadeClienteCreate, MensalidadeClienteResponse
from app.services import mensalidade_cliente_service

router = APIRouter(prefix="/api/mensalidades", tags=["Agenda - Mensalidades dos Clientes"])

@router.post("/", response_model=MensalidadeClienteResponse, status_code=status.HTTP_201_CREATED)
def criar_mensalidade(mensalidade: MensalidadeClienteCreate, db: Session = Depends(get_db)):
    return mensalidade_cliente_service.criar_mensalidade(db=db, mensalidade=mensalidade)

@router.get("/", response_model=List[MensalidadeClienteResponse])
def listar_mensalidades(db: Session = Depends(get_db)):
    return mensalidade_cliente_service.listar_mensalidades(db=db)

@router.get("/{mensalidade_id}", response_model=MensalidadeClienteResponse)
def obter_mensalidade(mensalidade_id: int, db: Session = Depends(get_db)):
    db_mensalidade = mensalidade_cliente_service.obter_mensalidade_por_id(db=db, mensalidade_id=mensalidade_id)
    if not db_mensalidade:
        raise HTTPException(status_code=404, detail="Mensalidade não encontrada")
    return db_mensalidade