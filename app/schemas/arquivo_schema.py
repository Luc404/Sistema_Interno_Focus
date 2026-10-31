from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.schemas.partial import PartialUpdate


class ArquivoCreate(BaseModel):
    titulo: str = Field(min_length=1, max_length=100)
    categoria: Optional[str] = Field(default=None, max_length=100)
    categoria_id: Optional[int] = None
    pasta_id: Optional[int] = None
    tipo_mime: str = Field(max_length=100)
    caminho_arquivo: str = Field(max_length=500)
    tamanho_bytes: int = Field(ge=0)
    usuario_id: Optional[int] = None


class ArquivoResponse(BaseModel):
    id: int
    titulo: str
    caminho_arquivo: str
    tipo_mime: str
    categoria: Optional[str] = None
    categoria_id: Optional[int] = None
    pasta_id: Optional[int] = None
    tamanho_bytes: int
    data_upload: datetime
    usuario_id: int

    class Config:
        from_attributes = True


class ArquivoUpdate(PartialUpdate):
    titulo: Optional[str] = Field(default=None, min_length=1, max_length=100)
    categoria: Optional[str] = Field(default=None, max_length=100)
    categoria_id: Optional[int] = None
    pasta_id: Optional[int] = None
