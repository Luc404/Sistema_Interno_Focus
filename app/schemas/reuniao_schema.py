from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, model_validator

from app.schemas.partial import PartialUpdate
from app.schemas.usuario_schema import UsuarioResumo


class ReuniaoCreate(BaseModel):
    titulo: str = Field(min_length=3, max_length=150)
    descricao: Optional[str] = Field(default=None, max_length=500)
    data_hora_inicio: datetime
    data_hora_fim: datetime
    link_reuniao: Optional[str] = Field(default=None, max_length=255)
    participantes_ids: list[int] = Field(default_factory=list)

    @model_validator(mode="after")
    def validar_periodo(self):
        if self.data_hora_fim <= self.data_hora_inicio:
            raise ValueError("A data/hora de fim deve ser posterior à de início")
        return self


class ReuniaoResponse(BaseModel):
    id: int
    titulo: str
    descricao: Optional[str] = None
    data_hora_inicio: datetime
    data_hora_fim: datetime
    link_reuniao: Optional[str] = None
    criador_id: int
    participantes: list[UsuarioResumo] = []

    class Config:
        from_attributes = True


class ReuniaoUpdate(PartialUpdate):
    titulo: Optional[str] = Field(default=None, min_length=3, max_length=150)
    descricao: Optional[str] = Field(default=None, max_length=500)
    data_hora_inicio: Optional[datetime] = None
    data_hora_fim: Optional[datetime] = None
    link_reuniao: Optional[str] = Field(default=None, max_length=255)
    participantes_ids: Optional[list[int]] = None
