"""Serviço de chatbots.

Gerencia o cadastro e a listagem de chatbots, o histórico de mensagens e o
envio de mensagens com geração de uma resposta simulada (regras por palavra-
chave), além de impedir interação com chatbots offline.
"""

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.model.chatbot import ChatMensagem, Chatbot
from app.schemas.chatbot_schema import ChatbotCreate
from app.services.common_service import montar_pagina, paginar


def obter_chatbot(db: Session, chatbot_id: int) -> Chatbot | None:
    """Busca um chatbot pelo ID.

    Args:
        db: Sessão do SQLAlchemy.
        chatbot_id: Identificador primário do chatbot.

    Returns:
        O chatbot encontrado ou ``None``.

    Raises:
        Nenhuma exceção de negócio; erros de banco são propagados.
    """
    return db.get(Chatbot, chatbot_id)


def listar_chatbots(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    busca: str | None = None,
    status_bot: str | None = None,
):
    """Lista chatbots com busca por texto, filtro de status e paginação.

    Args:
        db: Sessão do SQLAlchemy.
        skip: Offset da paginação.
        limit: Máximo de chatbots retornados.
        busca: Texto parcial pesquisado em nome e descrição.
        status_bot: Status exato do chatbot.

    Returns:
        Um objeto ``Page`` com os chatbots e o total filtrado.

    Raises:
        Nenhuma exceção de negócio; erros de banco são propagados.
    """
    query = db.query(Chatbot)
    if busca:
        termo = f"%{busca}%"
        # Pesquisa no nome OU na descrição, sem diferenciar maiúsculas.
        query = query.filter(Chatbot.nome.ilike(termo) | Chatbot.descricao.ilike(termo))
    if status_bot:
        query = query.filter(Chatbot.status == status_bot)
    query = query.order_by(Chatbot.nome)
    items, total = paginar(query, skip, limit)
    return montar_pagina(items, total, skip, limit)


def criar_chatbot(db: Session, dados: ChatbotCreate, criador_id: int) -> Chatbot:
    """Cria um novo chatbot.

    Args:
        db: Sessão do SQLAlchemy.
        dados: Dados de criação do chatbot.
        criador_id: ID do usuário criador.

    Returns:
        O chatbot persistido e recarregado do banco.

    Raises:
        Erros de banco são propagados.
    """
    chatbot = Chatbot(
        nome=dados.nome,
        descricao=dados.descricao,
        versao=dados.versao,
        status=dados.status,
        modelo=dados.modelo,
        criador_id=criador_id,
    )
    db.add(chatbot)
    db.commit()
    db.refresh(chatbot)
    return chatbot


def atualizar_chatbot(db: Session, chatbot: Chatbot, dados: dict) -> Chatbot:
    """Atualiza parcialmente um chatbot.

    Args:
        db: Sessão do SQLAlchemy.
        chatbot: Chatbot já carregado que será modificado.
        dados: Campos a alterar.

    Returns:
        O chatbot atualizado e recarregado do banco.

    Raises:
        Erros de banco são propagados.
    """
    # Aplica dinamicamente cada campo recebido.
    for campo, valor in dados.items():
        setattr(chatbot, campo, valor)
    db.commit()
    db.refresh(chatbot)
    return chatbot


def deletar_chatbot(db: Session, chatbot: Chatbot) -> None:
    """Remove um chatbot do banco.

    Args:
        db: Sessão do SQLAlchemy.
        chatbot: Chatbot a ser removido.

    Returns:
        ``None``.

    Raises:
        Erros de banco/integridade são propagados.
    """
    db.delete(chatbot)
    db.commit()


def listar_mensagens(
    db: Session,
    chatbot_id: int,
    skip: int = 0,
    limit: int = 100,
):
    """Lista o histórico de mensagens de um chatbot em ordem cronológica.

    Args:
        db: Sessão do SQLAlchemy.
        chatbot_id: ID do chatbot cujo histórico será listado.
        skip: Offset da paginação.
        limit: Máximo de mensagens retornadas.

    Returns:
        Um objeto ``Page`` com as mensagens e o total do chatbot.

    Raises:
        Nenhuma exceção de negócio; erros de banco são propagados.
    """
    query = (
        db.query(ChatMensagem)
        # Restringe ao chatbot informado.
        .filter(ChatMensagem.chatbot_id == chatbot_id)
        # Ordena da mensagem mais antiga para a mais recente.
        .order_by(ChatMensagem.criado_em)
    )
    items, total = paginar(query, skip, limit)
    return montar_pagina(items, total, skip, limit)


def _gerar_resposta(conteudo: str) -> str:
    """Gera uma resposta simulada com base em palavras-chave da mensagem.

    Não há integração com modelo de linguagem real: é um mecanismo de regras
    simples usado para simular o atendimento do chatbot.

    Args:
        conteudo: Texto enviado pelo usuário.

    Returns:
        A string de resposta correspondente à primeira regra que casar ou uma
        resposta genérica padrão.

    Raises:
        Nenhuma exceção.
    """
    # Normaliza para minúsculas para facilitar a comparação de palavras-chave.
    termo = conteudo.lower()
    if "jira" in termo or "ticket" in termo:
        return (
            "Perfeito. Registrei a solicitação e posso abrir um ticket no Jira "
            "com o resumo da conversa e os anexos relevantes."
        )
    if "log" in termo or "erro" in termo or "incidente" in termo:
        return (
            "Analisei o relato. Recomendo verificar os logs do serviço, a saúde do "
            "cache e as métricas de latência antes de escalar o incidente."
        )
    if "mensalidade" in termo or "financeiro" in termo:
        return (
            "Posso ajudar com o módulo financeiro. Informe o cliente ou o período "
            "desejado para eu resumir as mensalidades pendentes."
        )
    return (
        "Entendido. Registrei sua mensagem e posso encaminhá-la para a equipe "
        "responsável ou transformar o pedido em uma tarefa no backlog."
    )


def enviar_mensagem(
    db: Session,
    chatbot: Chatbot,
    usuario_id: int,
    conteudo: str,
) -> tuple[ChatMensagem, ChatMensagem]:
    """Registra a mensagem do usuário e gera/persiste a resposta do chatbot.

    Args:
        db: Sessão do SQLAlchemy.
        chatbot: Chatbot que receberá a mensagem.
        usuario_id: ID do usuário que enviou a mensagem.
        conteudo: Texto da mensagem.

    Returns:
        Uma tupla ``(mensagem_usuario, resposta)`` com ambos os registros já
        persistidos e recarregados do banco.

    Raises:
        HTTPException: 409 quando o chatbot está offline.
    """
    # Chatbots offline não aceitam novas mensagens.
    if chatbot.status == "OFFLINE":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Este chatbot está offline",
        )

    mensagem_usuario = ChatMensagem(
        chatbot_id=chatbot.id,
        usuario_id=usuario_id,
        papel="USER",
        conteudo=conteudo,
    )
    db.add(mensagem_usuario)
    # flush envia o INSERT sem encerrar a transação, garantindo que a mensagem
    # do usuário exista antes de criar a resposta na mesma transação.
    db.flush()

    resposta = ChatMensagem(
        chatbot_id=chatbot.id,
        usuario_id=usuario_id,
        papel="ASSISTANT",
        conteudo=_gerar_resposta(conteudo),
    )
    db.add(resposta)
    # Um único commit persiste as duas mensagens de forma atômica.
    db.commit()
    db.refresh(mensagem_usuario)
    db.refresh(resposta)
    return mensagem_usuario, resposta
