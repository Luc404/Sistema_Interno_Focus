from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field

from app.schemas.partial import PartialUpdate

StatusChatbot = Literal["ACTIVE", "ONLINE", "IDLE", "OFFLINE"]
PapelMensagem = Literal["USER", "ASSISTANT"]


class ChatbotCreate(BaseModel):
    nome: str = Field(min_length=2, max_length=120)
    descricao: Optional[str] = Field(default=None, max_length=255)
    versao: str = Field(default="v1.0", max_length=30)
    status: StatusChatbot = "OFFLINE"
    modelo: str = Field(default="gpt-4o", max_length=80)


class ChatbotResponse(BaseModel):
    id: int
    nome: str
    descricao: Optional[str] = None
    versao: str
    status: StatusChatbot
    modelo: str
    data_criacao: datetime
    criador_id: int

    class Config:
        from_attributes = True


class ChatbotUpdate(PartialUpdate):
    nome: Optional[str] = Field(default=None, min_length=2, max_length=120)
    descricao: Optional[str] = Field(default=None, max_length=255)
    versao: Optional[str] = Field(default=None, max_length=30)
    status: Optional[StatusChatbot] = None
    modelo: Optional[str] = Field(default=None, max_length=80)


class MensagemCreate(BaseModel):
    conteudo: str = Field(min_length=1, max_length=4000)


class ChatMensagemResponse(BaseModel):
    id: int
    chatbot_id: int
    usuario_id: int
    papel: PapelMensagem
    conteudo: str
    criado_em: datetime

    class Config:
        from_attributes = True


class ChatResposta(BaseModel):
    mensagem_usuario: ChatMensagemResponse
    resposta: ChatMensagemResponse
