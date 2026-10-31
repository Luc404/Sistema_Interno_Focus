from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.deps import ensure_owner_or_admin, get_current_user, require_perfis
from app.database import get_db
from app.model.usuario import Usuario
from app.schemas.common import Mensagem, Page
from app.schemas.usuario_schema import (
    UsuarioCreate,
    UsuarioResponse,
    UsuarioSelfUpdate,
    UsuarioUpdate,
)
from app.services import usuario_service

router = APIRouter(prefix="/api/usuarios", tags=["Usuários"])


@router.post("/", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
def criar_usuario(
    usuario: UsuarioCreate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_perfis("ADMIN")),
):
    return usuario_service.criar_usuario(db=db, usuario=usuario)


@router.get("/", response_model=Page[UsuarioResponse])
def listar_usuarios(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    busca: str | None = None,
    ativo: bool | None = None,
    setor_id: int | None = None,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_perfis("ADMIN")),
):
    return usuario_service.listar_usuarios(
        db=db,
        skip=skip,
        limit=limit,
        busca=busca,
        ativo=ativo,
        setor_id=setor_id,
    )


@router.get("/me", response_model=UsuarioResponse)
def obter_meu_usuario(usuario: Usuario = Depends(get_current_user)):
    return usuario


@router.patch("/me", response_model=UsuarioResponse)
def atualizar_meu_usuario(
    dados: UsuarioSelfUpdate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    return usuario_service.atualizar_usuario(
        db, usuario, dados.model_dump(exclude_unset=True)
    )


@router.get("/{usuario_id}", response_model=UsuarioResponse)
def obter_usuario(
    usuario_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    ensure_owner_or_admin(usuario, usuario_id)
    db_usuario = usuario_service.obter_usuario_por_id(db=db, usuario_id=usuario_id)
    if not db_usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return db_usuario


@router.patch("/{usuario_id}", response_model=UsuarioResponse)
def atualizar_usuario(
    usuario_id: int,
    dados: UsuarioUpdate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_perfis("ADMIN")),
):
    db_usuario = usuario_service.obter_usuario_por_id(db=db, usuario_id=usuario_id)
    if not db_usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return usuario_service.atualizar_usuario(
        db, db_usuario, dados.model_dump(exclude_unset=True)
    )


@router.post("/{usuario_id}/desativar", response_model=UsuarioResponse)
def desativar_usuario(
    usuario_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_perfis("ADMIN")),
):
    db_usuario = usuario_service.obter_usuario_por_id(db=db, usuario_id=usuario_id)
    if not db_usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return usuario_service.desativar_usuario(db, db_usuario)


@router.post("/{usuario_id}/ativar", response_model=UsuarioResponse)
def ativar_usuario(
    usuario_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_perfis("ADMIN")),
):
    db_usuario = usuario_service.obter_usuario_por_id(db=db, usuario_id=usuario_id)
    if not db_usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return usuario_service.reativar_usuario(db, db_usuario)


@router.delete("/{usuario_id}", response_model=Mensagem)
def deletar_usuario(
    usuario_id: int,
    db: Session = Depends(get_db),
    atual: Usuario = Depends(require_perfis("ADMIN")),
):
    if atual.id == usuario_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Você não pode desativar o próprio usuário",
        )
    db_usuario = usuario_service.obter_usuario_por_id(db=db, usuario_id=usuario_id)
    if not db_usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    usuario_service.desativar_usuario(db, db_usuario)
    return Mensagem(mensagem="Usuário desativado com sucesso")
