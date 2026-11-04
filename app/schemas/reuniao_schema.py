"""Schemas Pydantic de reuniões.

Cobre a criação, a resposta e a atualização parcial de reuniões, além
da validação que garante que o horário de fim seja posterior ao de
início e do vínculo com os participantes.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, model_validator

from app.schemas.partial import PartialUpdate
# Schema resumido de usuário usado para representar os participantes.
from app.schemas.usuario_schema import UsuarioResumo


class ReuniaoCreate(BaseModel):
    """Payload de entrada para criação de uma reunião."""

    # Título, entre 3 e 150 caracteres.
    titulo: str = Field(min_length=3, max_length=150)
    # Descrição opcional, até 500 caracteres.
    descricao: Optional[str] = Field(default=None, max_length=500)
    # Início da reunião.
    data_hora_inicio: datetime
    # Fim da reunião (deve ser posterior ao início).
    data_hora_fim: datetime
    # Link de acesso à reunião (ex.: videoconferência); opcional.
    link_reuniao: Optional[str] = Field(default=None, max_length=255)
    # IDs dos participantes; usa lista vazia como padrão seguro.
    participantes_ids: list[int] = Field(default_factory=list)

    @model_validator(mode="after")
    def validar_periodo(self):
        """Valida se ``data_hora_fim`` é posterior a ``data_hora_inicio``.

        Roda após a validação dos campos e rejeita períodos inválidos
        (fim igual ou anterior ao início).
        """
        if self.data_hora_fim <= self.data_hora_inicio:
            raise ValueError("A data/hora de fim deve ser posterior à de início")
        return self


class ReuniaoResponse(BaseModel):
    """Modelo de saída com os dados de uma reunião."""

    id: int
    titulo: str
    descricao: Optional[str] = None
    data_hora_inicio: datetime
    data_hora_fim: datetime
    link_reuniao: Optional[str] = None
    # Usuário que criou a reunião.
    criador_id: int
    # Participantes expandidos como resumos de usuário.
    participantes: list[UsuarioResumo] = []

    class Config:
        # Permite construir o schema a partir de objetos ORM.
        from_attributes = True


class ReuniaoUpdate(PartialUpdate):
    """Payload de atualização parcial de uma reunião.

    Todos os campos são opcionais; a validação de período não é repetida
    aqui porque pode ser aplicada na camada de serviço após combinar os
    valores enviados com os já existentes.
    """

    titulo: Optional[str] = Field(default=None, min_length=3, max_length=150)
    descricao: Optional[str] = Field(default=None, max_length=500)
    data_hora_inicio: Optional[datetime] = None
    data_hora_fim: Optional[datetime] = None
    link_reuniao: Optional[str] = Field(default=None, max_length=255)
    participantes_ids: Optional[list[int]] = None
