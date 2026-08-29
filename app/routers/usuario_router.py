from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

from app.schemas.usuario_schema import UsuarioCreate, UsuarioResponse
from app.database import get_db
from app.services import usuario_service

router = APIRouter(
    prefix="/api/usuarios",
    tags=["Usuários"]
)

@router.post("/", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
def criar_usuario(usuario: UsuarioCreate, db: Session = Depends(get_db)):
    return usuario_service.criar_usuario(db=db, usuario=usuario)

@router.get("/", response_model=List[UsuarioResponse])
def listar_usuarios(db: Session = Depends(get_db)):
    return usuario_service.listar_usuarios(db=db)

@router.get("/{usuario_id}", response_model=UsuarioResponse)
def obter_usuario(usuario_id: int, db: Session = Depends(get_db)):
    db_usuario = usuario_service.obter_usuario_por_id(db=db, usuario_id=usuario_id)
    if not db_usuario:
        raise HTTPException(status_code=404, detail="Usuário Não Encontrado")
    return db_usuario