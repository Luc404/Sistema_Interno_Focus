"""Router do dashboard.

Fornece o resumo consolidado de indicadores exibidos na tela inicial,
calculado conforme o usuário autenticado (escopo/permissões).

Endpoints expostos (prefixo ``/api/dashboard``):
- ``GET /resumo`` -> resumo consolidado do dashboard.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.database import get_db
from app.model.usuario import Usuario
from app.schemas.dashboard_schema import DashboardResumo
from app.services import dashboard_service

# Prefixo e tag OpenAPI das rotas do dashboard.
router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


@router.get("/resumo", response_model=DashboardResumo)
def obter_resumo(
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    """Retorna o resumo consolidado exibido no dashboard.

    Autenticação: obrigatória; o usuário é usado pelo serviço para limitar os
    dados ao seu escopo.
    Retorno: ``DashboardResumo`` com os indicadores agregados.
    """
    return dashboard_service.resumo(db, usuario)
