from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, require_perfis
from app.database import get_db
from app.model.usuario import Usuario
from app.schemas.chatbot_schema import (
    ChatbotCreate,
    ChatbotResponse,
    ChatbotUpdate,
    ChatMensagemResponse,
    ChatResposta,
    MensagemCreate,
)
from app.schemas.common import Mensagem, Page
from app.services import chatbot_service

router = APIRouter(prefix="/api/chatbots", tags=["Chatbots"])


@router.post("/", response_model=ChatbotResponse, status_code=status.HTTP_201_CREATED)
def criar_chatbot(
    dados: ChatbotCreate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(require_perfis("ADMIN")),
):
    return chatbot_service.criar_chatbot(db, dados, usuario.id)


@router.get("/", response_model=Page[ChatbotResponse])
def listar_chatbots(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    busca: str | None = None,
    status_bot: str | None = Query(None, alias="status"),
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    return chatbot_service.listar_chatbots(
        db, skip=skip, limit=limit, busca=busca, status_bot=status_bot
    )


@router.get("/{chatbot_id}", response_model=ChatbotResponse)
def obter_chatbot(
    chatbot_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    chatbot = chatbot_service.obter_chatbot(db, chatbot_id)
    if not chatbot:
        raise HTTPException(status_code=404, detail="Chatbot não encontrado")
    return chatbot


@router.patch("/{chatbot_id}", response_model=ChatbotResponse)
def atualizar_chatbot(
    chatbot_id: int,
    dados: ChatbotUpdate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_perfis("ADMIN")),
):
    chatbot = chatbot_service.obter_chatbot(db, chatbot_id)
    if not chatbot:
        raise HTTPException(status_code=404, detail="Chatbot não encontrado")
    return chatbot_service.atualizar_chatbot(db, chatbot, dados.model_dump(exclude_unset=True))


@router.delete("/{chatbot_id}", response_model=Mensagem)
def deletar_chatbot(
    chatbot_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_perfis("ADMIN")),
):
    chatbot = chatbot_service.obter_chatbot(db, chatbot_id)
    if not chatbot:
        raise HTTPException(status_code=404, detail="Chatbot não encontrado")
    chatbot_service.deletar_chatbot(db, chatbot)
    return Mensagem(mensagem="Chatbot excluído com sucesso")


@router.get("/{chatbot_id}/mensagens", response_model=Page[ChatMensagemResponse])
def listar_mensagens(
    chatbot_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    chatbot = chatbot_service.obter_chatbot(db, chatbot_id)
    if not chatbot:
        raise HTTPException(status_code=404, detail="Chatbot não encontrado")
    return chatbot_service.listar_mensagens(db, chatbot_id, skip, limit)


@router.post("/{chatbot_id}/mensagens", response_model=ChatResposta)
def enviar_mensagem(
    chatbot_id: int,
    dados: MensagemCreate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    chatbot = chatbot_service.obter_chatbot(db, chatbot_id)
    if not chatbot:
        raise HTTPException(status_code=404, detail="Chatbot não encontrado")
    mensagem_usuario, resposta = chatbot_service.enviar_mensagem(
        db, chatbot, usuario.id, dados.conteudo
    )
    return ChatResposta(mensagem_usuario=mensagem_usuario, resposta=resposta)
