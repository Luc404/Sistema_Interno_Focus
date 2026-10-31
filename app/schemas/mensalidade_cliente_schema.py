from datetime import datetime
from decimal import Decimal
from typing import Literal, Optional

from pydantic import BaseModel, Field, field_serializer

from app.schemas.partial import PartialUpdate

StatusMensalidade = Literal["PENDENTE", "PAGO", "ATRASADO"]


class MensalidadeClienteCreate(BaseModel):
    nome_cliente: str = Field(min_length=2, max_length=150)
    valor: Decimal = Field(gt=0, max_digits=10, decimal_places=2)
    data_vencimento: datetime
    status_pagamento: StatusMensalidade = "PENDENTE"
    observacao: Optional[str] = Field(default=None, max_length=255)


class MensalidadeClienteResponse(BaseModel):
    id: int
    nome_cliente: str
    valor: Decimal
    data_vencimento: datetime
    data_pagamento: Optional[datetime] = None
    status_pagamento: StatusMensalidade
    observacao: Optional[str] = None

    class Config:
        from_attributes = True

    @field_serializer("valor")
    def serializar_valor(self, valor: Decimal) -> float:
        return float(valor)


class MensalidadeClienteUpdate(PartialUpdate):
    nome_cliente: Optional[str] = Field(default=None, min_length=2, max_length=150)
    valor: Optional[Decimal] = Field(default=None, gt=0, max_digits=10, decimal_places=2)
    data_vencimento: Optional[datetime] = None
    status_pagamento: Optional[StatusMensalidade] = None
    observacao: Optional[str] = Field(default=None, max_length=255)


class MensalidadePagarRequest(BaseModel):
    data_pagamento: Optional[datetime] = None
    observacao: Optional[str] = Field(default=None, max_length=255)


class MensalidadeResumo(BaseModel):
    total: int
    pendentes: int
    pagas: int
    atrasadas: int
    valor_total_pendente: float
    valor_total_recebido: float
