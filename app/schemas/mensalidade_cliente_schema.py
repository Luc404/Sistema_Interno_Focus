from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.schemas.partial import PartialUpdate

class MensalidadeClienteCreate(BaseModel):
    nome_cliente: str
    valor: float
    data_vencimento: datetime
    status_pagamento: Optional[str] = "PENDENTE"  # ex: PENDENTE, PAGO, ATRASADO
    observacao: Optional[str] = None

class MensalidadeClienteResponse(BaseModel):
    id: int
    nome_cliente: str
    valor: float
    data_vencimento: datetime
    status_pagamento: str
    observacao: Optional[str] = None

    class Config:
        from_attributes = True

class MensalidadeClienteUpdate(PartialUpdate):
    nome_cliente: Optional[str] = None
    valor: Optional[float] = None
    data_vencimento: Optional[datetime] = None
    status_pagamento: Optional[str] = "PENDENTE"
    observacao: Optional[str] = None