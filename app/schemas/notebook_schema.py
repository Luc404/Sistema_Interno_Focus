from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.schemas.partial import PartialUpdate


class NotebookCreate(BaseModel):
    grupo: str = Field(default="PERSONAL NOTES", max_length=80)
    titulo: str = Field(min_length=2, max_length=150)
    subtitulo: Optional[str] = Field(default=None, max_length=255)
    conteudo: str = Field(min_length=1)
    tags: Optional[str] = Field(default=None, max_length=255)


class NotebookResponse(BaseModel):
    id: int
    grupo: str
    titulo: str
    subtitulo: Optional[str] = None
    conteudo: str
    tags: Optional[str] = None
    data_criacao: datetime
    data_atualizacao: datetime
    autor_id: int

    class Config:
        from_attributes = True


class NotebookUpdate(PartialUpdate):
    grupo: Optional[str] = Field(default=None, max_length=80)
    titulo: Optional[str] = Field(default=None, min_length=2, max_length=150)
    subtitulo: Optional[str] = Field(default=None, max_length=255)
    conteudo: Optional[str] = Field(default=None, min_length=1)
    tags: Optional[str] = Field(default=None, max_length=255)
