from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.schemas.arquivo_schema import ArquivoCreate, ArquivoResponse
from app.services import arquivo_service

router = APIRouter(
    prefix="/api/arquivos",
    tags=["Biblioteca - Arquivos"]
)

@router.post("/", response_model=ArquivoResponse, status_code=status.HTTP_201_CREATED)
def cadastrar_arquivo(arquivo: ArquivoCreate, db: Session = Depends(get_db)):
    return arquivo_service.criar_arquivo(db=db, arquivo_dto=arquivo)

@router.get("/", response_model=List[ArquivoResponse])
def listar_arquivos(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return arquivo_service.buscar_arquivos(db=db, skip=skip, limit=limit)

@router.get("/{arquivo_id}", response_model=ArquivoResponse)
def obter_arquivo(arquivo_id: int, db: Session = Depends(get_db)):
    db_arquivo = arquivo_service.buscar_arquivos_por_id(db=db, arquivo_id=arquivo_id)
    if not db_arquivo:
        raise HTTPException(status_code=404, detail="Arquivo não encontrado")
    return db_arquivo
