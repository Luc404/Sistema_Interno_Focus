from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.schemas.partial import PartialUpdate

class SetorCreate(BaseModel):
    nome: str
    descricao: Optional[str] = None

class SetorResponse(BaseModel):
    id: int
    nome: str
    descricao: Optional[str] = None
    status: Optional[str] = "ATIVO" #ATIVO OU INATIVO
    data_criacao: datetime

    class Config:
        from_attributes = True

class SetorUpdate(PartialUpdate):
    nome: Optional[str] = None
    descricao: Optional[str] = None
    status: Optional[str] = "ATIVO"
    