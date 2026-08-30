from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class TarefaPessoalCreate(BaseModel):
    titulo: str
    descricao: Optional[str] = None
    data_limite: datetime
    status: Optional[str] = "PENDENTE"
    usuario_id: int

class TarefaPessoalResponse(BaseModel):
    id: int
    titulo: str
    descricao: Optional[str] = None
    data_limite: datetime
    status: Optional[str] = "PENDENTE"
    usuario_id: int

    class Config:
        from_attributes = True