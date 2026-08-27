from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class TarefaBase(BaseModel):
    titulo: str
    descricao: Optional[str] = None
    data_limite: Optional[datetime] = None

class TarefaCreate(TarefaBase):
    usuario_id: int

class TarefaResponse(TarefaBase):
    id: int
    usuario_int: int
    status: str

    class Config:
        from_attributes = True