"""Schemas Pydantic de chatbots e suas conversas.

Cobre o cadastro/atualização de chatbots, o envio de mensagens pelo
usuário, o registro de mensagens (usuário/assistente) e o par
pergunta/resposta retornado em uma interação.
"""

from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field

from app.schemas.partial import PartialUpdate

# Estados possíveis de um chatbot.
StatusChatbot = Literal["ACTIVE", "ONLINE", "IDLE", "OFFLINE"]
# Papéis possíveis em uma mensagem de conversa.
PapelMensagem = Literal["USER", "ASSISTANT"]


class ChatbotCreate(BaseModel):
    """Payload de entrada para criação de um chatbot."""

    nome: str = Field(min_length=2, max_length=120)
    descricao: Optional[str] = Field(default=None, max_length=255)
    # Versão do bot; padrão "v1.0" quando não informada.
    versao: str = Field(default="v1.0", max_length=30)
    # Status inicial; padrão "OFFLINE".
    status: StatusChatbot = "OFFLINE"
    # Modelo de IA utilizado; padrão "gpt-4o".
    modelo: str = Field(default="gpt-4o", max_length=80)


class ChatbotResponse(BaseModel):
    """Modelo de saída com os dados de um chatbot."""

    id: int
    nome: str
    descricao: Optional[str] = None
    versao: str
    status: StatusChatbot
    modelo: str
    # Data/hora de criação do registro.
    data_criacao: datetime
    # Usuário que criou o chatbot.
    criador_id: int

    class Config:
        # Permite construir o schema a partir de objetos ORM.
        from_attributes = True


class ChatbotUpdate(PartialUpdate):
    """Payload de atualização parcial de um chatbot."""

    nome: Optional[str] = Field(default=None, min_length=2, max_length=120)
    descricao: Optional[str] = Field(default=None, max_length=255)
    versao: Optional[str] = Field(default=None, max_length=30)
    status: Optional[StatusChatbot] = None
    modelo: Optional[str] = Field(default=None, max_length=80)


class MensagemCreate(BaseModel):
    """Payload com o conteúdo da mensagem enviada pelo usuário."""

    # Texto da mensagem, entre 1 e 4000 caracteres.
    conteudo: str = Field(min_length=1, max_length=4000)


class ChatMensagemResponse(BaseModel):
    """Modelo de saída de uma mensagem persistida da conversa."""

    id: int
    # Chatbot ao qual a mensagem pertence.
    chatbot_id: int
    # Usuário autor da mensagem.
    usuario_id: int
    # Papel da mensagem: usuário ou assistente.
    papel: PapelMensagem
    conteudo: str
    # Data/hora de criação da mensagem.
    criado_em: datetime

    class Config:
        # Permite construir o schema a partir de objetos ORM.
        from_attributes = True


class ChatResposta(BaseModel):
    """Par formado pela mensagem do usuário e pela resposta do assistente."""

    # Mensagem original enviada pelo usuário.
    mensagem_usuario: ChatMensagemResponse
    # Mensagem gerada pelo assistente em resposta.
    resposta: ChatMensagemResponse
