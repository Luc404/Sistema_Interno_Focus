from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.model.chatbot import ChatMensagem, Chatbot
from app.schemas.chatbot_schema import ChatbotCreate
from app.services.common_service import montar_pagina, paginar


def obter_chatbot(db: Session, chatbot_id: int) -> Chatbot | None:
    return db.get(Chatbot, chatbot_id)


def listar_chatbots(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    busca: str | None = None,
    status_bot: str | None = None,
):
    query = db.query(Chatbot)
    if busca:
        termo = f"%{busca}%"
        query = query.filter(Chatbot.nome.ilike(termo) | Chatbot.descricao.ilike(termo))
    if status_bot:
        query = query.filter(Chatbot.status == status_bot)
    query = query.order_by(Chatbot.nome)
    items, total = paginar(query, skip, limit)
    return montar_pagina(items, total, skip, limit)


def criar_chatbot(db: Session, dados: ChatbotCreate, criador_id: int) -> Chatbot:
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
    for campo, valor in dados.items():
        setattr(chatbot, campo, valor)
    db.commit()
    db.refresh(chatbot)
    return chatbot


def deletar_chatbot(db: Session, chatbot: Chatbot) -> None:
    db.delete(chatbot)
    db.commit()


def listar_mensagens(
    db: Session,
    chatbot_id: int,
    skip: int = 0,
    limit: int = 100,
):
    query = (
        db.query(ChatMensagem)
        .filter(ChatMensagem.chatbot_id == chatbot_id)
        .order_by(ChatMensagem.criado_em)
    )
    items, total = paginar(query, skip, limit)
    return montar_pagina(items, total, skip, limit)


def _gerar_resposta(conteudo: str) -> str:
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
    db.flush()

    resposta = ChatMensagem(
        chatbot_id=chatbot.id,
        usuario_id=usuario_id,
        papel="ASSISTANT",
        conteudo=_gerar_resposta(conteudo),
    )
    db.add(resposta)
    db.commit()
    db.refresh(mensagem_usuario)
    db.refresh(resposta)
    return mensagem_usuario, resposta
