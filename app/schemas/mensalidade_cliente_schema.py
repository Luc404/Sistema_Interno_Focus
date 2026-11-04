"""Schemas Pydantic de mensalidades de clientes.

Trata do cadastro, resposta, atualização parcial, registro de pagamento
e resumo financeiro das mensalidades. Usa ``Decimal`` para valores
monetários, garantindo precisão, e serializa o valor como ``float`` na
saída da API.
"""

from datetime import datetime
from decimal import Decimal
from typing import Literal, Optional

from pydantic import BaseModel, Field, field_serializer

from app.schemas.partial import PartialUpdate

# Situações possíveis de uma mensalidade.
StatusMensalidade = Literal["PENDENTE", "PAGO", "ATRASADO"]


class MensalidadeClienteCreate(BaseModel):
    """Payload de entrada para criação de uma mensalidade."""

    # Nome do cliente, entre 2 e 150 caracteres.
    nome_cliente: str = Field(min_length=2, max_length=150)
    # Valor em Decimal, maior que zero, com até 10 dígitos e 2 casas.
    valor: Decimal = Field(gt=0, max_digits=10, decimal_places=2)
    # Data de vencimento da mensalidade.
    data_vencimento: datetime
    # Status inicial; padrão "PENDENTE".
    status_pagamento: StatusMensalidade = "PENDENTE"
    # Observação opcional, até 255 caracteres.
    observacao: Optional[str] = Field(default=None, max_length=255)


class MensalidadeClienteResponse(BaseModel):
    """Modelo de saída com os dados de uma mensalidade."""

    id: int
    nome_cliente: str
    # Valor mantido como Decimal internamente.
    valor: Decimal
    # Data de vencimento.
    data_vencimento: datetime
    # Data efetiva do pagamento (None enquanto não paga).
    data_pagamento: Optional[datetime] = None
    status_pagamento: StatusMensalidade
    observacao: Optional[str] = None

    class Config:
        # Permite construir o schema a partir de objetos ORM.
        from_attributes = True

    @field_serializer("valor")
    def serializar_valor(self, valor: Decimal) -> float:
        """Serializa o ``Decimal`` como ``float`` no JSON de resposta.

        Evita que o valor seja enviado como string e mantém o formato
        numérico esperado pelo frontend.
        """
        return float(valor)


class MensalidadeClienteUpdate(PartialUpdate):
    """Payload de atualização parcial de uma mensalidade."""

    nome_cliente: Optional[str] = Field(default=None, min_length=2, max_length=150)
    # Mesmas restrições de valor da criação, agora opcional.
    valor: Optional[Decimal] = Field(default=None, gt=0, max_digits=10, decimal_places=2)
    data_vencimento: Optional[datetime] = None
    status_pagamento: Optional[StatusMensalidade] = None
    observacao: Optional[str] = Field(default=None, max_length=255)


class MensalidadePagarRequest(BaseModel):
    """Payload para registrar o pagamento de uma mensalidade."""

    # Data do pagamento; se omitida, a camada de serviço pode assumir "agora".
    data_pagamento: Optional[datetime] = None
    # Observação opcional registrada junto ao pagamento.
    observacao: Optional[str] = Field(default=None, max_length=255)


class MensalidadeResumo(BaseModel):
    """Agregado financeiro das mensalidades para exibição/resumo."""

    # Total de mensalidades.
    total: int
    # Quantidade pendente.
    pendentes: int
    # Quantidade paga.
    pagas: int
    # Quantidade atrasada.
    atrasadas: int
    # Soma dos valores pendentes de recebimento.
    valor_total_pendente: float
    # Soma dos valores já recebidos.
    valor_total_recebido: float
