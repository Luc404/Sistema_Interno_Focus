from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, require_perfis
from app.database import get_db
from app.model.usuario import Usuario
from app.schemas.common import Mensagem, Page
from app.schemas.notificacao_schema import NotificacaoCreate, NotificacaoResponse
from app.services import notificacao_service

router = APIRouter(prefix="/api/notificacoes", tags=["Notificações"])


@router.post("/", response_model=NotificacaoResponse, status_code=status.HTTP_201_CREATED)
def criar_notificacao(
    dados: NotificacaoCreate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_perfis("ADMIN")),
):
    return notificacao_service.criar_notificacao(db, dados)


@router.get("/minhas", response_model=Page[NotificacaoResponse])
def listar_minhas_notificacoes(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    lida: bool | None = None,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    return notificacao_service.listar_notificacoes(
        db, usuario.id, skip=skip, limit=limit, lida=lida
    )


@router.patch("/ler-todas", response_model=Mensagem)
def marcar_todas_como_lidas(
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    quantidade = notificacao_service.marcar_todas_lidas(db, usuario.id)
    return Mensagem(mensagem=f"{quantidade} notificação(ões) marcada(s) como lida(s)")


@router.get("/{notificacao_id}", response_model=NotificacaoResponse)
def obter_notificacao(
    notificacao_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    notificacao = notificacao_service.obter_notificacao(db, notificacao_id)
    if not notificacao:
        raise HTTPException(status_code=404, detail="Notificação não encontrada")
    notificacao_service.validar_proprietario(notificacao, usuario.id)
    return notificacao


@router.patch("/{notificacao_id}/ler", response_model=NotificacaoResponse)
def marcar_como_lida(
    notificacao_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    notificacao = notificacao_service.obter_notificacao(db, notificacao_id)
    if not notificacao:
        raise HTTPException(status_code=404, detail="Notificação não encontrada")
    notificacao_service.validar_proprietario(notificacao, usuario.id)
    return notificacao_service.marcar_lida(db, notificacao)


@router.delete("/{notificacao_id}", response_model=Mensagem)
def deletar_notificacao(
    notificacao_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    notificacao = notificacao_service.obter_notificacao(db, notificacao_id)
    if not notificacao:
        raise HTTPException(status_code=404, detail="Notificação não encontrada")
    notificacao_service.validar_proprietario(notificacao, usuario.id)
    notificacao_service.deletar_notificacao(db, notificacao)
    return Mensagem(mensagem="Notificação excluída com sucesso")
