from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class LinkBase(BaseModel):
    titulo: str
    url: str
    descricao: Optional[str] = None

class LinkCreate(LinkBase):
    usuario_id: int

class LinkResponse(LinkBase):
    id: int
    usuario_id: int
    data_criacao: datetime

    class Config:
        from_attributes = True
