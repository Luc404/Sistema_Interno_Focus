from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.schemas.backlog_schema import BacklogCreate, BacklogResponse
from app.services import backlog_service

router = APIRouter(prefix="/api/backlog", tags=["Backlog"])

@router.post("/", response_model=BacklogResponse, status_code=status.HTTP_201_CREATED)
def criar_item_backlog(item: BacklogCreate, db: Session = Depends(get_db)):
    return backlog_service.criar_item(db=db, item=item)

@router.get("/", response_model=List[BacklogResponse])
def listar_itens_backlog(db: Session = Depends(get_db)):
    return backlog_service.listar_itens(db=db)

@router.get("/{item_id}", response_model=BacklogResponse)
def obter_item_backlog(item_id: int, db: Session = Depends(get_db)):
    db_item = backlog_service.obter_item_por_id(db=db, item_id=item_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Item do backlog não encontrado")
    return db_item