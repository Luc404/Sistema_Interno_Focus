from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class MensalidadeBase(BaseModel):
    nome_cliente: str
    valor: float
    data_vencimento: datetime
    observacao: Optional[str] = None

class MensalidadeCreate(MensalidadeBase):
    pass

class MensalidadeResponse(MensalidadeBase):
    id: int
    status_pagamento: str

    class Config:
        from_attributes = True
