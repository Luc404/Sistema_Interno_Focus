from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.schemas.link_schema import LinkCreate, LinkResponse
from app.services import link_service

router = APIRouter(prefix="/api/links", tags=["Biblioteca - Links Úteis"])

@router.post("/", response_model=LinkResponse, status_code=status.HTTP_201_CREATED)
def criar_link(link: LinkCreate, db: Session = Depends(get_db)):
    return link_service.criar_link(db=db, link=link)

@router.get("/", response_model=List[LinkResponse])
def listar_links(db: Session = Depends(get_db)):
    return link_service.listar_links(db=db)

@router.get("/{link_id}", response_model=LinkResponse)
def obter_link(link_id: int, db: Session = Depends(get_db)):
    db_link = link_service.obter_link_por_id(db=db, link_id=link_id)
    if not db_link:
        raise HTTPException(status_code=404, detail="Link não encontrado")
    return db_link