"""Router de setores.

Permite criar, listar com filtros, consultar, atualizar e excluir setores da
organização. Operações de escrita exigem perfil ADMIN; leitura exige usuário
autenticado.

Endpoints expostos (prefixo ``/api/setores``):
- ``POST /``             -> cria setor (ADMIN);
- ``GET /``              -> listagem paginada com filtros;
- ``GET /{setor_id}``    -> consulta setor;
- ``PATCH /{setor_id}``  -> atualização parcial (ADMIN);
- ``DELETE /{setor_id}`` -> exclusão (ADMIN).
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, require_perfis
from app.database import get_db
from app.model.usuario import Usuario
from app.schemas.common import Mensagem, Page
from app.schemas.setor_schema import SetorCreate, SetorResponse, SetorUpdate
from app.services import setor_service

# Prefixo e tag OpenAPI das rotas de setores.
router = APIRouter(prefix="/api/setores", tags=["Setores"])


@router.post("/", response_model=SetorResponse, status_code=status.HTTP_201_CREATED)
def criar_setor(
    setor: SetorCreate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_perfis("ADMIN")),
):
    """Cria um novo setor.

    Autenticação/permissão: exige perfil ADMIN.
    Retorno: ``SetorResponse`` criado (HTTP 201).
    """
    return setor_service.criar_setor(db=db, setor=setor)


@router.get("/", response_model=Page[SetorResponse])
def listar_setores(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    busca: str | None = None,
    status_setor: str | None = Query(None, alias="status"),
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    """Lista setores com paginação, busca e filtro de status.

    O filtro de status é exposto como query ``status`` via ``alias``.
    ``skip``/``limit`` controlam a paginação (máximo de 500 por página).

    Autenticação: qualquer usuário autenticado.
    Retorno: ``Page[SetorResponse]``.
    """
    return setor_service.listar_setores(
        db=db,
        skip=skip,
        limit=limit,
        busca=busca,
        status_setor=status_setor,
    )


@router.get("/{setor_id}", response_model=SetorResponse)
def obter_setor(
    setor_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    """Consulta um setor pelo identificador.

    Autenticação: qualquer usuário autenticado.
    Retorno: ``SetorResponse`` ou HTTP 404 se não existir.
    """
    db_setor = setor_service.obter_setor_por_id(db=db, setor_id=setor_id)
    if not db_setor:
        raise HTTPException(status_code=404, detail="Setor não encontrado")
    return db_setor


@router.patch("/{setor_id}", response_model=SetorResponse)
def atualizar_setor(
    setor_id: int,
    dados: SetorUpdate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_perfis("ADMIN")),
):
    """Atualiza parcialmente um setor.

    Apenas campos enviados são aplicados (``exclude_unset=True``).
    Autenticação/permissão: exige perfil ADMIN.
    Retorno: ``SetorResponse`` atualizado; HTTP 404 se não existir.
    """
    db_setor = setor_service.obter_setor_por_id(db=db, setor_id=setor_id)
    if not db_setor:
        raise HTTPException(status_code=404, detail="Setor não encontrado")
    return setor_service.atualizar_setor(db, db_setor, dados.model_dump(exclude_unset=True))


@router.delete("/{setor_id}", response_model=Mensagem)
def deletar_setor(
    setor_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_perfis("ADMIN")),
):
    """Exclui um setor.

    Autenticação/permissão: exige perfil ADMIN.
    Retorno: ``Mensagem`` de confirmação; HTTP 404 se não existir.
    """
    db_setor = setor_service.obter_setor_por_id(db=db, setor_id=setor_id)
    if not db_setor:
        raise HTTPException(status_code=404, detail="Setor não encontrado")
    setor_service.deletar_setor(db, db_setor)
    return Mensagem(mensagem="Setor excluído com sucesso")
