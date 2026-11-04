"""Serviço de notificações.

Gerencia a listagem por usuário, criação individual e em lote, marcação de
leitura (individual ou em massa), exclusão e verificação de propriedade para
garantir que cada usuário só acesse suas próprias notificações.
"""

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.model.notificacao import Notificacao
from app.schemas.notificacao_schema import NotificacaoCreate
from app.services.common_service import montar_pagina, paginar


def obter_notificacao(db: Session, notificacao_id: int) -> Notificacao | None:
    """Busca uma notificação pelo ID.

    Args:
        db: Sessão do SQLAlchemy.
        notificacao_id: Identificador primário da notificação.

    Returns:
        A notificação encontrada ou ``None``.

    Raises:
        Nenhuma exceção de negócio; erros de banco são propagados.
    """
    return db.get(Notificacao, notificacao_id)


def listar_notificacoes(
    db: Session,
    usuario_id: int,
    skip: int = 0,
    limit: int = 100,
    lida: bool | None = None,
):
    """Lista notificações de um usuário, com filtro opcional de leitura.

    Args:
        db: Sessão do SQLAlchemy.
        usuario_id: ID do usuário dono das notificações.
        skip: Offset da paginação.
        limit: Máximo de notificações retornadas.
        lida: Quando informado, filtra por lidas (True) ou não lidas (False).

    Returns:
        Um objeto ``Page`` com as notificações e o total filtrado.

    Raises:
        Nenhuma exceção de negócio; erros de banco são propagados.
    """
    # Sempre restringe ao usuário; o filtro de leitura é opcional.
    query = db.query(Notificacao).filter(Notificacao.usuario_id == usuario_id)
    if lida is not None:
        query = query.filter(Notificacao.lida == lida)
    # Mais recentes primeiro.
    query = query.order_by(Notificacao.data_criacao.desc())
    items, total = paginar(query, skip, limit)
    return montar_pagina(items, total, skip, limit)


def criar_notificacao(db: Session, dados: NotificacaoCreate) -> Notificacao:
    """Cria uma notificação para um usuário específico.

    Args:
        db: Sessão do SQLAlchemy.
        dados: Dados de criação da notificação.

    Returns:
        A notificação persistida e recarregada do banco.

    Raises:
        Erros de banco são propagados.
    """
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
    """Cria a mesma notificação para vários usuários em lote.

    Args:
        db: Sessão do SQLAlchemy.
        usuario_ids: IDs dos usuários que receberão a notificação.
        titulo: Título da notificação.
        mensagem: Conteúdo da notificação.
        tipo: Tipo/categoria da notificação (padrão ``INFO``).
        link: Link opcional associado à notificação.

    Returns:
        ``None``.

    Raises:
        Erros de banco são propagados.
    """
    # ``set`` remove IDs duplicados, evitando notificações repetidas.
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
    # Um único commit persiste todas as notificações do lote.
    db.commit()


def marcar_lida(db: Session, notificacao: Notificacao) -> Notificacao:
    """Marca uma notificação como lida.

    Args:
        db: Sessão do SQLAlchemy.
        notificacao: Notificação já carregada.

    Returns:
        A notificação atualizada e recarregada do banco.

    Raises:
        Erros de banco são propagados.
    """
    notificacao.lida = True
    db.commit()
    db.refresh(notificacao)
    return notificacao


def marcar_todas_lidas(db: Session, usuario_id: int) -> int:
    """Marca todas as notificações não lidas de um usuário como lidas.

    Args:
        db: Sessão do SQLAlchemy.
        usuario_id: ID do usuário.

    Returns:
        A quantidade de notificações efetivamente atualizadas.

    Raises:
        Erros de banco são propagados.
    """
    # UPDATE em massa evita carregar cada registro individualmente.
    quantidade = (
        db.query(Notificacao)
        .filter(Notificacao.usuario_id == usuario_id, Notificacao.lida.is_(False))
        .update({Notificacao.lida: True})
    )
    db.commit()
    return quantidade


def deletar_notificacao(db: Session, notificacao: Notificacao) -> None:
    """Remove uma notificação do banco.

    Args:
        db: Sessão do SQLAlchemy.
        notificacao: Notificação a ser removida.

    Returns:
        ``None``.

    Raises:
        Erros de banco são propagados.
    """
    db.delete(notificacao)
    db.commit()


def validar_proprietario(notificacao: Notificacao, usuario_id: int) -> None:
    """Garante que a notificação pertence ao usuário informado.

    Args:
        notificacao: Notificação a ser verificada.
        usuario_id: ID do usuário autenticado.

    Returns:
        ``None`` quando a propriedade é válida.

    Raises:
        HTTPException: 403 quando a notificação pertence a outro usuário.
    """
    if notificacao.usuario_id != usuario_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não tem permissão para acessar esta notificação",
        )
