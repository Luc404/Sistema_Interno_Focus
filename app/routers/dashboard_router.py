from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.database import get_db
from app.model.usuario import Usuario
from app.schemas.dashboard_schema import DashboardResumo
from app.services import dashboard_service

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


@router.get("/resumo", response_model=DashboardResumo)
def obter_resumo(
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    return dashboard_service.resumo(db, usuario)
