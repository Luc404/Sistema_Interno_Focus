from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.model.agenda import Reuniao
from app.model.usuario import Usuario
from app.schemas.reuniao_schema import ReuniaoCreate
from app.services.common_service import montar_pagina, paginar


def obter_reuniao_por_id(db: Session, reuniao_id: int) -> Reuniao | None:
    return db.get(Reuniao, reuniao_id)


def listar_reunioes(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    busca: str | None = None,
    data_inicio: datetime | None = None,
    data_fim: datetime | None = None,
    criador_id: int | None = None,
    participante_id: int | None = None,
):
    query = db.query(Reuniao)
    if busca:
        termo = f"%{busca}%"
        query = query.filter(Reuniao.titulo.ilike(termo) | Reuniao.descricao.ilike(termo))
    if data_inicio:
        query = query.filter(Reuniao.data_hora_inicio >= data_inicio)
    if data_fim:
        query = query.filter(Reuniao.data_hora_inicio <= data_fim)
    if criador_id is not None:
        query = query.filter(Reuniao.criador_id == criador_id)
    if participante_id is not None:
        query = query.filter(Reuniao.participantes.any(Usuario.id == participante_id))

    query = query.order_by(Reuniao.data_hora_inicio)
    items, total = paginar(query, skip, limit)
    return montar_pagina(items, total, skip, limit)


def listar_proximas(db: Session, limite: int = 5) -> list[Reuniao]:
    agora = datetime.now(timezone.utc)
    return (
        db.query(Reuniao)
        .filter(Reuniao.data_hora_inicio >= agora)
        .order_by(Reuniao.data_hora_inicio)
        .limit(limite)
        .all()
    )


def _buscar_participantes(db: Session, ids: list[int]) -> list[Usuario]:
    if not ids:
        return []
    participantes = db.query(Usuario).filter(Usuario.id.in_(ids)).all()
    encontrados = {p.id for p in participantes}
    faltantes = set(ids) - encontrados
    if faltantes:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Participantes não encontrados: {sorted(faltantes)}",
        )
    return participantes


def _verificar_conflito(
    db: Session,
    inicio: datetime,
    fim: datetime,
    usuario_ids: list[int],
    ignorar_reuniao_id: int | None = None,
) -> None:
    if not usuario_ids:
        return
    query = db.query(Reuniao).filter(
        Reuniao.data_hora_inicio < fim,
        Reuniao.data_hora_fim > inicio,
        or_(
            Reuniao.criador_id.in_(usuario_ids),
            Reuniao.participantes.any(Usuario.id.in_(usuario_ids)),
        ),
    )
    if ignorar_reuniao_id is not None:
        query = query.filter(Reuniao.id != ignorar_reuniao_id)
    if query.first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Existe conflito de horário com outra reunião para um dos participantes",
        )


def criar_reuniao(db: Session, reuniao: ReuniaoCreate, criador_id: int) -> Reuniao:
    participantes = _buscar_participantes(db, reuniao.participantes_ids)
    ids_envolvidos = list({criador_id, *reuniao.participantes_ids})
    _verificar_conflito(db, reuniao.data_hora_inicio, reuniao.data_hora_fim, ids_envolvidos)

    db_reuniao = Reuniao(
        titulo=reuniao.titulo,
        descricao=reuniao.descricao,
        data_hora_inicio=reuniao.data_hora_inicio,
        data_hora_fim=reuniao.data_hora_fim,
        link_reuniao=reuniao.link_reuniao,
        criador_id=criador_id,
        participantes=participantes,
    )
    db.add(db_reuniao)
    db.commit()
    db.refresh(db_reuniao)
    return db_reuniao


def atualizar_reuniao(db: Session, db_reuniao: Reuniao, dados: dict) -> Reuniao:
    participantes_ids = dados.pop("participantes_ids", None)
    inicio = dados.get("data_hora_inicio", db_reuniao.data_hora_inicio)
    fim = dados.get("data_hora_fim", db_reuniao.data_hora_fim)
    if fim <= inicio:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A data/hora de fim deve ser posterior à de início",
        )

    if participantes_ids is not None:
        participantes = _buscar_participantes(db, participantes_ids)
        db_reuniao.participantes = participantes
        ids_envolvidos = list({db_reuniao.criador_id, *participantes_ids})
        _verificar_conflito(db, inicio, fim, ids_envolvidos, ignorar_reuniao_id=db_reuniao.id)
    elif "data_hora_inicio" in dados or "data_hora_fim" in dados:
        ids_envolvidos = [db_reuniao.criador_id, *[p.id for p in db_reuniao.participantes]]
        _verificar_conflito(db, inicio, fim, ids_envolvidos, ignorar_reuniao_id=db_reuniao.id)

    for campo, valor in dados.items():
        setattr(db_reuniao, campo, valor)

    db.commit()
    db.refresh(db_reuniao)
    return db_reuniao


def adicionar_participante(db: Session, db_reuniao: Reuniao, usuario: Usuario) -> Reuniao:
    if usuario not in db_reuniao.participantes:
        db_reuniao.participantes.append(usuario)
        db.commit()
        db.refresh(db_reuniao)
    return db_reuniao


def remover_participante(db: Session, db_reuniao: Reuniao, usuario: Usuario) -> Reuniao:
    if usuario in db_reuniao.participantes:
        db_reuniao.participantes.remove(usuario)
        db.commit()
        db.refresh(db_reuniao)
    return db_reuniao


def deletar_reuniao(db: Session, db_reuniao: Reuniao) -> None:
    db.delete(db_reuniao)
    db.commit()
