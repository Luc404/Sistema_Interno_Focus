from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class ReuniaoBase(BaseModel):
    titulo: str
    data_hora_inicio: datetime
    data_hora_fim: datetime
    descricao: Optional[str] = None
    link_reuniao: Optional[str] = None

class ReuniaoCreate(ReuniaoBase):
    criador_id: int
    participantes_ids: List[int] = []

class ReuniaoResponse(ReuniaoBase):
    id: int
    criador_id: int
    class Config:
        from_attributes = True