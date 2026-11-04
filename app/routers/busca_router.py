"""Router da busca global.

Executa uma pesquisa textual unificada em múltiplos recursos do sistema e
retorna os resultados agrupados, respeitando o escopo/permissões do usuário.

Endpoints expostos (prefixo ``/api/busca``):
- ``GET /`` -> busca global por termo, com limite de resultados por recurso.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.database import get_db
from app.model.usuario import Usuario
from app.schemas.busca_schema import RespostaBusca
from app.services import busca_service

# Prefixo e tag OpenAPI das rotas de busca.
router = APIRouter(prefix="/api/busca", tags=["Busca Global"])


@router.get("/", response_model=RespostaBusca)
def buscar(
    q: str = Query(..., min_length=2, max_length=100),
    limite: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    """Realiza a busca global pelo termo informado.

    Parâmetros:
    - ``q``: termo de busca obrigatório, com 2 a 100 caracteres;
    - ``limite``: quantidade máxima de resultados por categoria (1 a 50).

    Autenticação: obrigatória; o usuário é repassado ao serviço para aplicar
    restrições de visibilidade dos resultados.

    Retorno: ``RespostaBusca`` com os resultados agrupados.
    """
    return busca_service.buscar(db, q, limite, usuario)
