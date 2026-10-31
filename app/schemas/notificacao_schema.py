from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field

TipoNotificacao = Literal["INFO", "ALERTA", "SUCESSO", "REUNIAO", "TAREFA", "FINANCEIRO"]


class NotificacaoCreate(BaseModel):
    usuario_id: int
    titulo: str = Field(min_length=2, max_length=150)
    mensagem: str = Field(min_length=2, max_length=500)
    tipo: TipoNotificacao = "INFO"
    link: Optional[str] = Field(default=None, max_length=255)


class NotificacaoResponse(BaseModel):
    id: int
    titulo: str
    mensagem: str
    tipo: TipoNotificacao
    link: Optional[str] = None
    lida: bool
    data_criacao: datetime
    usuario_id: int

    class Config:
        from_attributes = True
