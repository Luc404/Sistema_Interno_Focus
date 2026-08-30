from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class SetorCreate(BaseModel):
    nome: str
    descricao: Optional[str] = None

class SetorResponse(BaseModel):
    id: int
    nome: str
    descricao: Optional[str] = None
    ativo: bool
    data_criacao: datetime

    class Config:
        from_attributes = True