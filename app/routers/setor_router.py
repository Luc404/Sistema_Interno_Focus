from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.schemas.setor_schema import SetorCreate, SetorResponse
from app.services import setor_service

router = APIRouter(prefix="/api/setores", tags=["Setores"])

@router.post("/", response_model=SetorResponse, status_code=status.HTTP_201_CREATED)
def criar_setor(setor: SetorCreate, db: Session = Depends(get_db)):
    db_setor = setor_service.obter_setor_por_nome(db, nome=setor.nome)
    if db_setor:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Já existe um setor cadastrado com este nome."
        )
    return setor_service.criar_setor(db=db, setor=setor)

@router.get("/", response_model=List[SetorResponse])
def listar_setores(db: Session = Depends(get_db)):
    return setor_service.listar_setores(db=db)

@router.get("/{setor_id}", response_model=SetorResponse)
def obter_setor(setor_id: int, db: Session = Depends(get_db)):
    db_setor = setor_service.obter_setor_por_id(db=db, setor_id=setor_id)
    if not db_setor:
        raise HTTPException(status_code=404, detail="Setor não encontrado")
    return db_setor