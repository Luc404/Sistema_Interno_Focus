from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, require_perfis
from app.database import get_db
from app.model.usuario import Usuario
from app.schemas.common import Mensagem, Page
from app.schemas.setor_schema import SetorCreate, SetorResponse, SetorUpdate
from app.services import setor_service

router = APIRouter(prefix="/api/setores", tags=["Setores"])


@router.post("/", response_model=SetorResponse, status_code=status.HTTP_201_CREATED)
def criar_setor(
    setor: SetorCreate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_perfis("ADMIN")),
):
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
    db_setor = setor_service.obter_setor_por_id(db=db, setor_id=setor_id)
    if not db_setor:
        raise HTTPException(status_code=404, detail="Setor não encontrado")
    setor_service.deletar_setor(db, db_setor)
    return Mensagem(mensagem="Setor excluído com sucesso")
