from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.model.notificacao import Notificacao
from app.schemas.notificacao_schema import NotificacaoCreate
from app.services.common_service import montar_pagina, paginar


def obter_notificacao(db: Session, notificacao_id: int) -> Notificacao | None:
    return db.get(Notificacao, notificacao_id)


def listar_notificacoes(
    db: Session,
    usuario_id: int,
    skip: int = 0,
    limit: int = 100,
    lida: bool | None = None,
):
    query = db.query(Notificacao).filter(Notificacao.usuario_id == usuario_id)
    if lida is not None:
        query = query.filter(Notificacao.lida == lida)
    query = query.order_by(Notificacao.data_criacao.desc())
    items, total = paginar(query, skip, limit)
    return montar_pagina(items, total, skip, limit)


def criar_notificacao(db: Session, dados: NotificacaoCreate) -> Notificacao:
    notificacao = Notificacao(
        usuario_id=dados.usuario_id,
        titulo=dados.titulo,
        mensagem=dados.mensagem,
        tipo=dados.tipo,
        link=dados.link,
    )
    db.add(notificacao)
    db.commit()
    db.refresh(notificacao)
    return notificacao


def criar_para_usuarios(
    db: Session,
    usuario_ids: list[int],
    titulo: str,
    mensagem: str,
    tipo: str = "INFO",
    link: str | None = None,
) -> None:
    for usuario_id in set(usuario_ids):
        db.add(
            Notificacao(
                usuario_id=usuario_id,
                titulo=titulo,
                mensagem=mensagem,
                tipo=tipo,
                link=link,
            )
        )
    db.commit()


def marcar_lida(db: Session, notificacao: Notificacao) -> Notificacao:
    notificacao.lida = True
    db.commit()
    db.refresh(notificacao)
    return notificacao


def marcar_todas_lidas(db: Session, usuario_id: int) -> int:
    quantidade = (
        db.query(Notificacao)
        .filter(Notificacao.usuario_id == usuario_id, Notificacao.lida.is_(False))
        .update({Notificacao.lida: True})
    )
    db.commit()
    return quantidade


def deletar_notificacao(db: Session, notificacao: Notificacao) -> None:
    db.delete(notificacao)
    db.commit()


def validar_proprietario(notificacao: Notificacao, usuario_id: int) -> None:
    if notificacao.usuario_id != usuario_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não tem permissão para acessar esta notificação",
        )
