from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.database import get_db
from app.model.usuario import Usuario
from app.schemas.busca_schema import RespostaBusca
from app.services import busca_service

router = APIRouter(prefix="/api/busca", tags=["Busca Global"])


@router.get("/", response_model=RespostaBusca)
def buscar(
    q: str = Query(..., min_length=2, max_length=100),
    limite: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    return busca_service.buscar(db, q, limite, usuario)
