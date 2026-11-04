"""Schemas Pydantic de notificações.

Define os tipos de notificação aceitos e os modelos de criação e
resposta, incluindo estado de leitura e vínculo com o usuário
destinatário.
"""

from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field

# Categorias possíveis de notificação.
TipoNotificacao = Literal["INFO", "ALERTA", "SUCESSO", "REUNIAO", "TAREFA", "FINANCEIRO"]


class NotificacaoCreate(BaseModel):
    """Payload de entrada para criação de uma notificação."""

    # Usuário que receberá a notificação (chave estrangeira).
    usuario_id: int
    # Título, entre 2 e 150 caracteres.
    titulo: str = Field(min_length=2, max_length=150)
    # Mensagem, entre 2 e 500 caracteres.
    mensagem: str = Field(min_length=2, max_length=500)
    # Tipo da notificação; padrão "INFO".
    tipo: TipoNotificacao = "INFO"
    # Link opcional de destino ao clicar na notificação.
    link: Optional[str] = Field(default=None, max_length=255)


class NotificacaoResponse(BaseModel):
    """Modelo de saída com os dados de uma notificação."""

    id: int
    titulo: str
    mensagem: str
    tipo: TipoNotificacao
    link: Optional[str] = None
    # Indica se a notificação já foi lida pelo usuário.
    lida: bool
    # Data/hora de criação.
    data_criacao: datetime
    # Usuário destinatário.
    usuario_id: int

    class Config:
        # Permite construir o schema a partir de objetos ORM.
        from_attributes = True
