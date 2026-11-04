"""Router de chatbots e conversas.

Gerencia o cadastro de chatbots (administração), a listagem/consulta de bots e
o histórico de mensagens, além do envio de mensagens que gera uma resposta do
bot e a persiste na conversa do usuário.

Endpoints expostos (prefixo ``/api/chatbots``):
- ``POST /``                            -> cria chatbot (ADMIN);
- ``GET /``                             -> lista chatbots;
- ``GET /{chatbot_id}``                 -> consulta chatbot;
- ``PATCH /{chatbot_id}``               -> atualiza chatbot (ADMIN);
- ``DELETE /{chatbot_id}``              -> exclui chatbot (ADMIN);
- ``GET /{chatbot_id}/mensagens``       -> histórico paginado;
- ``POST /{chatbot_id}/mensagens``      -> envia mensagem e recebe resposta.
"""

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

# Prefixo e tag OpenAPI das rotas de chatbots.
router = APIRouter(prefix="/api/chatbots", tags=["Chatbots"])


@router.post("/", response_model=ChatbotResponse, status_code=status.HTTP_201_CREATED)
def criar_chatbot(
    dados: ChatbotCreate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(require_perfis("ADMIN")),
):
    """Cria um novo chatbot, registrando o usuário criador.

    Autenticação/permissão: exige perfil ADMIN.
    Retorno: ``ChatbotResponse`` criado (HTTP 201).
    """
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
    """Lista chatbots com paginação, busca e filtro de status.

    O filtro de status é exposto como query ``status`` via ``alias``.
    ``skip``/``limit`` controlam a paginação (máximo de 500 por página).

    Autenticação: qualquer usuário autenticado.
    Retorno: ``Page[ChatbotResponse]``.
    """
    return chatbot_service.listar_chatbots(
        db, skip=skip, limit=limit, busca=busca, status_bot=status_bot
    )


@router.get("/{chatbot_id}", response_model=ChatbotResponse)
def obter_chatbot(
    chatbot_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    """Consulta um chatbot pelo identificador.

    Autenticação: qualquer usuário autenticado.
    Retorno: ``ChatbotResponse`` ou HTTP 404 se não existir.
    """
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
    """Atualiza parcialmente um chatbot.

    Apenas campos enviados são aplicados (``exclude_unset=True``).
    Autenticação/permissão: exige perfil ADMIN.
    Retorno: ``ChatbotResponse`` atualizado; HTTP 404 se não existir.
    """
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
    """Exclui um chatbot.

    Autenticação/permissão: exige perfil ADMIN.
    Retorno: ``Mensagem`` de confirmação; HTTP 404 se não existir.
    """
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
    """Lista o histórico de mensagens de um chatbot, de forma paginada.

    ``skip``/``limit`` controlam a paginação (máximo de 500 por página).
    Autenticação: qualquer usuário autenticado.
    Retorno: ``Page[ChatMensagemResponse]``; HTTP 404 se o bot não existir.
    """
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
    """Envia uma mensagem do usuário ao chatbot e retorna a resposta gerada.

    A mensagem do usuário e a resposta do bot são persistidas pelo serviço,
    associadas ao usuário autenticado.

    Autenticação: obrigatória.
    Retorno: ``ChatResposta`` contendo a mensagem do usuário e a resposta;
    HTTP 404 se o chatbot não existir.
    """
    chatbot = chatbot_service.obter_chatbot(db, chatbot_id)
    if not chatbot:
        raise HTTPException(status_code=404, detail="Chatbot não encontrado")
    mensagem_usuario, resposta = chatbot_service.enviar_mensagem(
        db, chatbot, usuario.id, dados.conteudo
    )
    return ChatResposta(mensagem_usuario=mensagem_usuario, resposta=resposta)
