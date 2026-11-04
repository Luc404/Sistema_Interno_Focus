"""Serviço de reuniões.

Gerencia listagem/filtros e CRUD de reuniões, validação de participantes,
detecção de conflitos de horário (considerando criador e participantes) e
inclusão/remoção de participantes em reuniões existentes.
"""

from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.model.agenda import Reuniao
from app.model.usuario import Usuario
from app.schemas.reuniao_schema import ReuniaoCreate
from app.services.common_service import montar_pagina, paginar


def obter_reuniao_por_id(db: Session, reuniao_id: int) -> Reuniao | None:
    """Busca uma reunião pelo ID.

    Args:
        db: Sessão do SQLAlchemy.
        reuniao_id: Identificador primário da reunião.

    Returns:
        A reunião encontrada ou ``None``.

    Raises:
        Nenhuma exceção de negócio; erros de banco são propagados.
    """
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
    """Lista reuniões com filtros de texto, período, criador e participante.

    Args:
        db: Sessão do SQLAlchemy.
        skip: Offset da paginação.
        limit: Máximo de reuniões retornadas.
        busca: Texto parcial pesquisado em título e descrição.
        data_inicio: Limite inferior (inclusivo) do início da reunião.
        data_fim: Limite superior (inclusivo) do início da reunião.
        criador_id: ID do criador da reunião.
        participante_id: ID de um participante que deve estar na reunião.

    Returns:
        Um objeto ``Page`` com as reuniões e o total filtrado.

    Raises:
        Nenhuma exceção de negócio; erros de banco são propagados.
    """
    query = db.query(Reuniao)
    if busca:
        termo = f"%{busca}%"
        # Pesquisa no título OU na descrição.
        query = query.filter(Reuniao.titulo.ilike(termo) | Reuniao.descricao.ilike(termo))
    if data_inicio:
        query = query.filter(Reuniao.data_hora_inicio >= data_inicio)
    if data_fim:
        query = query.filter(Reuniao.data_hora_inicio <= data_fim)
    if criador_id is not None:
        query = query.filter(Reuniao.criador_id == criador_id)
    if participante_id is not None:
        # ``any`` gera EXISTS sobre a relação many-to-many de participantes.
        query = query.filter(Reuniao.participantes.any(Usuario.id == participante_id))

    # Ordena cronologicamente pelo início.
    query = query.order_by(Reuniao.data_hora_inicio)
    items, total = paginar(query, skip, limit)
    return montar_pagina(items, total, skip, limit)


def listar_proximas(db: Session, limite: int = 5) -> list[Reuniao]:
    """Retorna as próximas reuniões a partir do momento atual.

    Args:
        db: Sessão do SQLAlchemy.
        limite: Quantidade máxima de reuniões a retornar.

    Returns:
        Lista de reuniões futuras ordenadas cronologicamente.

    Raises:
        Erros de banco são propagados.
    """
    agora = datetime.now(timezone.utc)
    return (
        db.query(Reuniao)
        # Apenas reuniões cujo início ainda não passou.
        .filter(Reuniao.data_hora_inicio >= agora)
        .order_by(Reuniao.data_hora_inicio)
        .limit(limite)
        .all()
    )


def _buscar_participantes(db: Session, ids: list[int]) -> list[Usuario]:
    """Carrega os usuários participantes a partir de uma lista de IDs.

    Args:
        db: Sessão do SQLAlchemy.
        ids: IDs dos participantes desejados.

    Returns:
        Lista de usuários encontrados (vazia se ``ids`` estiver vazia).

    Raises:
        HTTPException: 404 quando algum ID informado não existe, listando os
            IDs faltantes de forma ordenada.
    """
    # Lista vazia: não há nada a validar nem buscar.
    if not ids:
        return []
    participantes = db.query(Usuario).filter(Usuario.id.in_(ids)).all()
    # Conjunto dos IDs efetivamente encontrados.
    encontrados = {p.id for p in participantes}
    # Diferença entre os IDs pedidos e os encontrados.
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
    """Verifica se há sobreposição de horário para algum dos usuários.

    Duas reuniões conflitam quando uma começa antes do fim da outra e termina
    depois do início da outra. A verificação considera tanto criadores quanto
    participantes das reuniões existentes.

    Args:
        db: Sessão do SQLAlchemy.
        inicio: Início da reunião que está sendo criada/atualizada.
        fim: Fim da reunião que está sendo criada/atualizada.
        usuario_ids: Usuários envolvidos (criador + participantes).
        ignorar_reuniao_id: ID de reunião a desconsiderar (a própria reunião
            em atualizações).

    Returns:
        ``None`` quando não há conflito.

    Raises:
        HTTPException: 409 quando existe conflito de horário.
    """
    if not usuario_ids:
        return
    query = db.query(Reuniao).filter(
        # Sobreposição de intervalos: início existente < fim novo E
        # fim existente > início novo.
        Reuniao.data_hora_inicio < fim,
        Reuniao.data_hora_fim > inicio,
        # O usuário é criador OU participante da reunião existente.
        or_(
            Reuniao.criador_id.in_(usuario_ids),
            Reuniao.participantes.any(Usuario.id.in_(usuario_ids)),
        ),
    )
    # Em updates, ignora a própria reunião para não conflitar consigo mesma.
    if ignorar_reuniao_id is not None:
        query = query.filter(Reuniao.id != ignorar_reuniao_id)
    if query.first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Existe conflito de horário com outra reunião para um dos participantes",
        )


def criar_reuniao(db: Session, reuniao: ReuniaoCreate, criador_id: int) -> Reuniao:
    """Cria uma reunião validando participantes e conflitos de horário.

    Args:
        db: Sessão do SQLAlchemy.
        reuniao: Dados de criação da reunião.
        criador_id: ID do usuário criador.

    Returns:
        A reunião persistida e recarregada do banco.

    Raises:
        HTTPException: 404 para participante inexistente e 409 para conflito
            de horário.
    """
    # Valida e carrega os usuários participantes informados.
    participantes = _buscar_participantes(db, reuniao.participantes_ids)
    # O criador também ocupa o horário, então entra na checagem de conflito.
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
    """Atualiza parcialmente uma reunião, revalidando conflitos quando preciso.

    Args:
        db: Sessão do SQLAlchemy.
        db_reuniao: Reunião já carregada que será modificada.
        dados: Campos a alterar (pode conter ``participantes_ids``).

    Returns:
        A reunião atualizada e recarregada do banco.

    Raises:
        HTTPException: 400 quando o fim não é posterior ao início, 404 para
            participante inexistente e 409 para conflito de horário.
    """
    # Remove ``participantes_ids`` do dicionário para tratá-lo separadamente;
    # os demais campos podem ser aplicados diretamente via setattr.
    participantes_ids = dados.pop("participantes_ids", None)
    # Usa os novos horários quando enviados ou mantém os atuais.
    inicio = dados.get("data_hora_inicio", db_reuniao.data_hora_inicio)
    fim = dados.get("data_hora_fim", db_reuniao.data_hora_fim)
    if fim <= inicio:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A data/hora de fim deve ser posterior à de início",
        )

    if participantes_ids is not None:
        # Lista de participantes foi alterada: recarrega e substitui a relação.
        participantes = _buscar_participantes(db, participantes_ids)
        db_reuniao.participantes = participantes
        ids_envolvidos = list({db_reuniao.criador_id, *participantes_ids})
        _verificar_conflito(db, inicio, fim, ids_envolvidos, ignorar_reuniao_id=db_reuniao.id)
    elif "data_hora_inicio" in dados or "data_hora_fim" in dados:
        # Apenas horários mudaram: considera criador + participantes atuais.
        ids_envolvidos = [db_reuniao.criador_id, *[p.id for p in db_reuniao.participantes]]
        _verificar_conflito(db, inicio, fim, ids_envolvidos, ignorar_reuniao_id=db_reuniao.id)

    # Aplica os demais campos atualizados.
    for campo, valor in dados.items():
        setattr(db_reuniao, campo, valor)

    db.commit()
    db.refresh(db_reuniao)
    return db_reuniao


def adicionar_participante(db: Session, db_reuniao: Reuniao, usuario: Usuario) -> Reuniao:
    """Adiciona um participante à reunião, evitando duplicidade.

    Args:
        db: Sessão do SQLAlchemy.
        db_reuniao: Reunião que receberá o participante.
        usuario: Usuário a ser adicionado.

    Returns:
        A reunião (atualizada quando houve inclusão).

    Raises:
        Erros de banco são propagados.
    """
    # Só persiste quando o usuário ainda não participa da reunião.
    if usuario not in db_reuniao.participantes:
        db_reuniao.participantes.append(usuario)
        db.commit()
        db.refresh(db_reuniao)
    return db_reuniao


def remover_participante(db: Session, db_reuniao: Reuniao, usuario: Usuario) -> Reuniao:
    """Remove um participante da reunião, se presente.

    Args:
        db: Sessão do SQLAlchemy.
        db_reuniao: Reunião da qual o participante será removido.
        usuario: Usuário a ser removido.

    Returns:
        A reunião (atualizada quando houve remoção).

    Raises:
        Erros de banco são propagados.
    """
    # Só persiste quando o usuário realmente está na relação.
    if usuario in db_reuniao.participantes:
        db_reuniao.participantes.remove(usuario)
        db.commit()
        db.refresh(db_reuniao)
    return db_reuniao


def deletar_reuniao(db: Session, db_reuniao: Reuniao) -> None:
    """Remove uma reunião do banco.

    Args:
        db: Sessão do SQLAlchemy.
        db_reuniao: Reunião a ser removida.

    Returns:
        ``None``.

    Raises:
        Erros de banco são propagados.
    """
    db.delete(db_reuniao)
    db.commit()
