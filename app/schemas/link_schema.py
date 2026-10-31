from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, HttpUrl

from app.schemas.partial import PartialUpdate


class LinkCreate(BaseModel):
    titulo: str = Field(min_length=2, max_length=160)
    url: HttpUrl
    descricao: Optional[str] = Field(default=None, max_length=255)
    categoria: Optional[str] = Field(default=None, max_length=100)


class LinkResponse(BaseModel):
    id: int
    titulo: str
    url: HttpUrl
    descricao: Optional[str] = None
    categoria: Optional[str] = None
    data_criacao: datetime
    usuario_id: int

    class Config:
        from_attributes = True


class LinkUpdate(PartialUpdate):
    titulo: Optional[str] = Field(default=None, min_length=2, max_length=160)
    url: Optional[HttpUrl] = None
    descricao: Optional[str] = Field(default=None, max_length=255)
    categoria: Optional[str] = Field(default=None, max_length=100)
