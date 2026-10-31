from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.schemas.partial import PartialUpdate
class BacklogCreate(BaseModel):
    titulo: str
    descricao: Optional[str] = None
    tipo: str
    prioridade: Optional[str] = "BAIXA"  # ex: BAIXA, MEDIA, ALTA
    status: Optional[str] = "PENDENTE"   # ex: PENDENTE, EM_ANDAMENTO, CONCLUIDO
    setor_id: Optional[int] = None
    autor_id: Optional[int] = None

class BacklogResponse(BaseModel):
    id: int
    titulo: str
    descricao: Optional[str] = None
    tipo: str
    prioridade: str
    status: str
    data_criacao: datetime
    setor_id: Optional[int] = None
    autor_id: Optional[int] = None

    class Config:
        from_attributes = True

class BacklogUpdate(PartialUpdate):
    titulo: Optional[str] = None
    descricao: Optional[str] = None
    tipo: Optional[str] = None
    prioridade: Optional[str] = "BAIXA"
    status: Optional[str] = "PENDENTE"
    setor_id: Optional[int] = None
    autor_id: Optional[int] = None