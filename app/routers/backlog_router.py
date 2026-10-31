from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.deps import ensure_owner_or_admin, get_current_user
from app.database import get_db
from app.model.usuario import Usuario
from app.schemas.backlog_schema import (
    BacklogCreate,
    BacklogResponse,
    BacklogStatusUpdate,
    BacklogUpdate,
)
from app.schemas.common import Mensagem, Page
from app.services import backlog_service

router = APIRouter(prefix="/api/backlog", tags=["Backlog"])


@router.post("/", response_model=BacklogResponse, status_code=status.HTTP_201_CREATED)
def criar_item_backlog(
    item: BacklogCreate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    return backlog_service.criar_item(db=db, item=item, autor_id=usuario.id)


@router.get("/", response_model=Page[BacklogResponse])
def listar_itens_backlog(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    busca: str | None = None,
    status_item: str | None = Query(None, alias="status"),
    tipo: str | None = None,
    prioridade: str | None = None,
    setor_id: int | None = None,
    autor_id: int | None = None,
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    return backlog_service.listar_itens(
        db=db,
        skip=skip,
        limit=limit,
        busca=busca,
        status_item=status_item,
        tipo=tipo,
        prioridade=prioridade,
        setor_id=setor_id,
        autor_id=autor_id,
    )


@router.get("/{item_id}", response_model=BacklogResponse)
def obter_item_backlog(
    item_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    db_item = backlog_service.obter_item_por_id(db=db, item_id=item_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Item do backlog não encontrado")
    return db_item


@router.patch("/{item_id}", response_model=BacklogResponse)
def atualizar_item_backlog(
    item_id: int,
    dados: BacklogUpdate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    db_item = backlog_service.obter_item_por_id(db=db, item_id=item_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Item do backlog não encontrado")
    ensure_owner_or_admin(usuario, db_item.autor_id)
    return backlog_service.atualizar_item(db, db_item, dados.model_dump(exclude_unset=True))


@router.patch("/{item_id}/status", response_model=BacklogResponse)
def alterar_status_backlog(
    item_id: int,
    dados: BacklogStatusUpdate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    db_item = backlog_service.obter_item_por_id(db=db, item_id=item_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Item do backlog não encontrado")
    ensure_owner_or_admin(usuario, db_item.autor_id)
    return backlog_service.mudar_status(db, db_item, dados.status)


@router.delete("/{item_id}", response_model=Mensagem)
def deletar_item_backlog(
    item_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    db_item = backlog_service.obter_item_por_id(db=db, item_id=item_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Item do backlog não encontrado")
    ensure_owner_or_admin(usuario, db_item.autor_id)
    backlog_service.deletar_item(db, db_item)
    return Mensagem(mensagem="Item do backlog excluído com sucesso")
