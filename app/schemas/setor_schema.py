from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field

from app.schemas.partial import PartialUpdate

StatusSetor = Literal["ATIVO", "INATIVO"]


class SetorCreate(BaseModel):
    nome: str = Field(min_length=2, max_length=100)
    descricao: Optional[str] = Field(default=None, max_length=255)


class SetorResponse(BaseModel):
    id: int
    nome: str
    descricao: Optional[str] = None
    status: StatusSetor
    data_criacao: datetime

    class Config:
        from_attributes = True


class SetorUpdate(PartialUpdate):
    nome: Optional[str] = Field(default=None, min_length=2, max_length=100)
    descricao: Optional[str] = Field(default=None, max_length=255)
    status: Optional[StatusSetor] = None
