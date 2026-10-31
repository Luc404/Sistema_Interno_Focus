from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field

from app.schemas.partial import PartialUpdate

StatusBacklog = Literal["PENDENTE", "EM_ANDAMENTO", "CONCLUIDO"]
PrioridadeBacklog = Literal["BAIXA", "MEDIA", "ALTA"]
TipoBacklog = Literal["FEATURE", "BUG", "MELHORIA", "INFRA", "OUTRO"]


class BacklogCreate(BaseModel):
    titulo: str = Field(min_length=3, max_length=150)
    descricao: Optional[str] = Field(default=None, max_length=500)
    tipo: TipoBacklog
    prioridade: PrioridadeBacklog = "MEDIA"
    status: StatusBacklog = "PENDENTE"
    setor_id: Optional[int] = None


class BacklogResponse(BaseModel):
    id: int
    titulo: str
    descricao: Optional[str] = None
    tipo: str
    prioridade: str
    status: str
    data_criacao: datetime
    setor_id: Optional[int] = None
    autor_id: int

    class Config:
        from_attributes = True


class BacklogUpdate(PartialUpdate):
    titulo: Optional[str] = Field(default=None, min_length=3, max_length=150)
    descricao: Optional[str] = Field(default=None, max_length=500)
    tipo: Optional[TipoBacklog] = None
    prioridade: Optional[PrioridadeBacklog] = None
    status: Optional[StatusBacklog] = None
    setor_id: Optional[int] = None


class BacklogStatusUpdate(BaseModel):
    status: StatusBacklog
