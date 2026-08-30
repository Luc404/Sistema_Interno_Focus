from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.schemas.reuniao_schema import ReuniaoCreate, ReuniaoResponse
from app.services import reuniao_service

router = APIRouter(prefix="/api/reunioes", tags=["Agenda - Reuniões"])

@router.post("/", response_model=ReuniaoResponse, status_code=status.HTTP_201_CREATED)
def criar_reuniao(reuniao: ReuniaoCreate, db: Session = Depends(get_db)):
    return reuniao_service.criar_reuniao(db=db, reuniao=reuniao)

@router.get("/", response_model=List[ReuniaoResponse])
def listar_reunioes(db: Session = Depends(get_db)):
    return reuniao_service.listar_reunioes(db=db)

@router.get("/{reuniao_id}", response_model=ReuniaoResponse)
def obter_reuniao(reuniao_id: int, db: Session = Depends(get_db)):
    db_reuniao = reuniao_service.obter_reuniao_por_id(db=db, reuniao_id=reuniao_id)
    if not db_reuniao:
        raise HTTPException(status_code=404, detail="Reunião não encontrada")
    return db_reuniao