from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.deps import ensure_owner_or_admin, get_current_user
from app.database import get_db
from app.model.usuario import Usuario
from app.schemas.common import Mensagem, Page
from app.schemas.reuniao_schema import ReuniaoCreate, ReuniaoResponse, ReuniaoUpdate
from app.schemas.usuario_schema import UsuarioResumo
from app.services import notificacao_service, reuniao_service, usuario_service

router = APIRouter(prefix="/api/reunioes", tags=["Agenda - Reuniões"])


@router.post("/", response_model=ReuniaoResponse, status_code=status.HTTP_201_CREATED)
def criar_reuniao(
    reuniao: ReuniaoCreate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    db_reuniao = reuniao_service.criar_reuniao(db=db, reuniao=reuniao, criador_id=usuario.id)
    if reuniao.participantes_ids:
        notificacao_service.criar_para_usuarios(
            db,
            reuniao.participantes_ids,
            titulo="Nova reunião agendada",
            mensagem=f"Você foi convidado para a reunião: {reuniao.titulo}",
            tipo="REUNIAO",
            link=f"/agenda/reunioes/{db_reuniao.id}",
        )
    return db_reuniao


@router.get("/", response_model=Page[ReuniaoResponse])
def listar_reunioes(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    busca: str | None = None,
    data_inicio: datetime | None = None,
    data_fim: datetime | None = None,
    criador_id: int | None = None,
    participante_id: int | None = None,
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    return reuniao_service.listar_reunioes(
        db=db,
        skip=skip,
        limit=limit,
        busca=busca,
        data_inicio=data_inicio,
        data_fim=data_fim,
        criador_id=criador_id,
        participante_id=participante_id,
    )


@router.get("/proximas", response_model=list[ReuniaoResponse])
def listar_proximas_reunioes(
    limite: int = Query(5, ge=1, le=50),
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    return reuniao_service.listar_proximas(db, limite)


@router.get("/{reuniao_id}", response_model=ReuniaoResponse)
def obter_reuniao(
    reuniao_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    db_reuniao = reuniao_service.obter_reuniao_por_id(db=db, reuniao_id=reuniao_id)
    if not db_reuniao:
        raise HTTPException(status_code=404, detail="Reunião não encontrada")
    return db_reuniao


@router.patch("/{reuniao_id}", response_model=ReuniaoResponse)
def atualizar_reuniao(
    reuniao_id: int,
    dados: ReuniaoUpdate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    db_reuniao = reuniao_service.obter_reuniao_por_id(db=db, reuniao_id=reuniao_id)
    if not db_reuniao:
        raise HTTPException(status_code=404, detail="Reunião não encontrada")
    ensure_owner_or_admin(usuario, db_reuniao.criador_id)
    return reuniao_service.atualizar_reuniao(
        db, db_reuniao, dados.model_dump(exclude_unset=True)
    )


@router.delete("/{reuniao_id}", response_model=Mensagem)
def deletar_reuniao(
    reuniao_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    db_reuniao = reuniao_service.obter_reuniao_por_id(db=db, reuniao_id=reuniao_id)
    if not db_reuniao:
        raise HTTPException(status_code=404, detail="Reunião não encontrada")
    ensure_owner_or_admin(usuario, db_reuniao.criador_id)
    reuniao_service.deletar_reuniao(db, db_reuniao)
    return Mensagem(mensagem="Reunião excluída com sucesso")


@router.get("/{reuniao_id}/participantes", response_model=list[UsuarioResumo])
def listar_participantes(
    reuniao_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    db_reuniao = reuniao_service.obter_reuniao_por_id(db=db, reuniao_id=reuniao_id)
    if not db_reuniao:
        raise HTTPException(status_code=404, detail="Reunião não encontrada")
    return db_reuniao.participantes


@router.post("/{reuniao_id}/participantes/{usuario_id}", response_model=ReuniaoResponse)
def adicionar_participante(
    reuniao_id: int,
    usuario_id: int,
    db: Session = Depends(get_db),
    atual: Usuario = Depends(get_current_user),
):
    db_reuniao = reuniao_service.obter_reuniao_por_id(db=db, reuniao_id=reuniao_id)
    if not db_reuniao:
        raise HTTPException(status_code=404, detail="Reunião não encontrada")
    ensure_owner_or_admin(atual, db_reuniao.criador_id)
    participante = usuario_service.obter_usuario_por_id(db, usuario_id)
    if not participante:
        raise HTTPException(status_code=404, detail="Participante não encontrado")
    db_reuniao = reuniao_service.adicionar_participante(db, db_reuniao, participante)
    notificacao_service.criar_para_usuarios(
        db,
        [usuario_id],
        titulo="Convite para reunião",
        mensagem=f"Você foi adicionado à reunião: {db_reuniao.titulo}",
        tipo="REUNIAO",
        link=f"/agenda/reunioes/{db_reuniao.id}",
    )
    return db_reuniao


@router.delete("/{reuniao_id}/participantes/{usuario_id}", response_model=ReuniaoResponse)
def remover_participante(
    reuniao_id: int,
    usuario_id: int,
    db: Session = Depends(get_db),
    atual: Usuario = Depends(get_current_user),
):
    db_reuniao = reuniao_service.obter_reuniao_por_id(db=db, reuniao_id=reuniao_id)
    if not db_reuniao:
        raise HTTPException(status_code=404, detail="Reunião não encontrada")
    ensure_owner_or_admin(atual, db_reuniao.criador_id)
    participante = usuario_service.obter_usuario_por_id(db, usuario_id)
    if not participante:
        raise HTTPException(status_code=404, detail="Participante não encontrado")
    return reuniao_service.remover_participante(db, db_reuniao, participante)
