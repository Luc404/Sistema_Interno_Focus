from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class BacklogBase(BaseModel):
    titulo: str
    descricao: str
    tipo: str
    prioridade: Optional[str] = "MEDIA"

class BacklogCreate(BacklogBase):
    autor_id: int
    setor_id: int

class BacklogResponse(BacklogCreate):
    id: int
    status: str
    data_criacao: datetime

    class Config:
        from_attributes = True