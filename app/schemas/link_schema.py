from pydantic import BaseModel, HttpUrl
from typing import Optional

class LinkCreate(BaseModel):
    titulo: str
    url: str
    descricao: Optional[str] = None
    usuario_id: Optional[int] = None

class LinkResponse(BaseModel):
    id: int
    titulo: str
    url: str
    descricao: Optional[str] = None
    usuario_id: Optional[int] = None

    class Config:
        from_attributes = True