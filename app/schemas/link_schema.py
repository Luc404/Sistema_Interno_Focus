from pydantic import BaseModel, HttpUrl
from typing import Optional
from app.schemas.partial import PartialUpdate
class LinkCreate(BaseModel):
    titulo: str
    url: HttpUrl
    descricao: Optional[str] = None
    usuario_id: Optional[int] = None

class LinkResponse(BaseModel):
    id: int
    titulo: str
    url: HttpUrl
    descricao: Optional[str] = None
    usuario_id: Optional[int] = None

    class Config:
        from_attributes = True

class LinkUpdate(PartialUpdate):
    titulo: Optional[str] = None
    url: Optional[HttpUrl] = None
    descricao: Optional[str] = None
    usuario_id: Optional[int] = None