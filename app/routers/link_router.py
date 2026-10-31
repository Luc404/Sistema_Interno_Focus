from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.deps import ensure_owner_or_admin, get_current_user
from app.database import get_db
from app.model.usuario import Usuario
from app.schemas.common import Mensagem, Page
from app.schemas.link_schema import LinkCreate, LinkResponse, LinkUpdate
from app.services import link_service

router = APIRouter(prefix="/api/links", tags=["Biblioteca - Links Úteis"])


@router.post("/", response_model=LinkResponse, status_code=status.HTTP_201_CREATED)
def criar_link(
    link: LinkCreate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    return link_service.criar_link(db=db, link=link, usuario_id=usuario.id)


@router.get("/", response_model=Page[LinkResponse])
def listar_links(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    busca: str | None = None,
    categoria: str | None = None,
    usuario_id: int | None = None,
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    return link_service.listar_links(
        db=db,
        skip=skip,
        limit=limit,
        busca=busca,
        categoria=categoria,
        usuario_id=usuario_id,
    )


@router.get("/{link_id}", response_model=LinkResponse)
def obter_link(
    link_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    db_link = link_service.obter_link_por_id(db=db, link_id=link_id)
    if not db_link:
        raise HTTPException(status_code=404, detail="Link não encontrado")
    return db_link


@router.patch("/{link_id}", response_model=LinkResponse)
def atualizar_link(
    link_id: int,
    dados: LinkUpdate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    db_link = link_service.obter_link_por_id(db=db, link_id=link_id)
    if not db_link:
        raise HTTPException(status_code=404, detail="Link não encontrado")
    ensure_owner_or_admin(usuario, db_link.usuario_id)
    return link_service.atualizar_link(db, db_link, dados.model_dump(exclude_unset=True))


@router.delete("/{link_id}", response_model=Mensagem)
def deletar_link(
    link_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    db_link = link_service.obter_link_por_id(db=db, link_id=link_id)
    if not db_link:
        raise HTTPException(status_code=404, detail="Link não encontrado")
    ensure_owner_or_admin(usuario, db_link.usuario_id)
    link_service.deletar_link(db, db_link)
    return Mensagem(mensagem="Link excluído com sucesso")
