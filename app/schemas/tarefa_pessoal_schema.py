from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field

from app.schemas.partial import PartialUpdate

StatusTarefa = Literal["PENDENTE", "EM_ANDAMENTO", "CONCLUIDA"]


class TarefaPessoalCreate(BaseModel):
    titulo: str = Field(min_length=3, max_length=150)
    descricao: Optional[str] = Field(default=None, max_length=500)
    data_limite: Optional[datetime] = None
    status: StatusTarefa = "PENDENTE"


class TarefaPessoalResponse(BaseModel):
    id: int
    titulo: str
    descricao: Optional[str] = None
    data_limite: Optional[datetime] = None
    status: StatusTarefa
    usuario_id: int

    class Config:
        from_attributes = True


class TarefaPessoalUpdate(PartialUpdate):
    titulo: Optional[str] = Field(default=None, min_length=3, max_length=150)
    descricao: Optional[str] = Field(default=None, max_length=500)
    data_limite: Optional[datetime] = None
    status: Optional[StatusTarefa] = None


class TarefaStatusUpdate(BaseModel):
    status: StatusTarefa
