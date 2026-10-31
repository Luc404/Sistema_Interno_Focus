from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from app.schemas.partial import PartialUpdate

class ArquivoBase(BaseModel):
    titulo: str
    categoria: str

class ArquivoCreate(ArquivoBase):
    tipo_mime: str
    caminho_arquivo: str
    tamanho_bytes: int
    usuario_id: int

class ArquivoResponse(ArquivoBase):
    id: int
    caminho_arquivo: str
    tipo_mime: str
    tamanho_bytes: int
    data_upload: datetime
    usuario_id: int

    class Config:
        from_attributes = True

class ArquivoUpdate(PartialUpdate):
    titulo: Optional[str] = None
    categoria: Optional[str] = None
    tipo_mime: Optional[str] = None
    caminho_arquivo: Optional[str] = None
    tamanho_bytes: Optional[int] = None
    usuario_id: Optional[int] = None