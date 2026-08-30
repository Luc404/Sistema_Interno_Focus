from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ReuniaoCreate(BaseModel):
    titulo: str
    descricao: Optional[str] = None
    data_hora_inicio: datetime
    data_hora_fim: datetime
    link_reuniao: Optional[str] = None
    criador_id: int

class ReuniaoResponse(BaseModel):
    id: int
    titulo: str
    descricao: Optional[str] = None
    data_hora_inicio: datetime
    data_hora_fim: datetime
    link_reuniao: Optional[str] = None
    criador_id: int

    class Config:
        from_attributes = True