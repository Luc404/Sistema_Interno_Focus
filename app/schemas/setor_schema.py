"""Schemas Pydantic de setores da organização.

Define os estados possíveis de um setor e os modelos de criação,
resposta e atualização parcial.
"""

from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field

from app.schemas.partial import PartialUpdate

# Situações possíveis de um setor.
StatusSetor = Literal["ATIVO", "INATIVO"]


class SetorCreate(BaseModel):
    """Payload de entrada para criação de um setor."""

    # Nome do setor, entre 2 e 100 caracteres.
    nome: str = Field(min_length=2, max_length=100)
    # Descrição opcional, até 255 caracteres.
    descricao: Optional[str] = Field(default=None, max_length=255)


class SetorResponse(BaseModel):
    """Modelo de saída com os dados de um setor."""

    id: int
    nome: str
    descricao: Optional[str] = None
    # Situação atual do setor.
    status: StatusSetor
    # Data/hora de criação do registro.
    data_criacao: datetime

    class Config:
        # Permite construir o schema a partir de objetos ORM.
        from_attributes = True


class SetorUpdate(PartialUpdate):
    """Payload de atualização parcial de um setor."""

    nome: Optional[str] = Field(default=None, min_length=2, max_length=100)
    descricao: Optional[str] = Field(default=None, max_length=255)
    # Permite ativar/inativar o setor.
    status: Optional[StatusSetor] = None
