from pydantic import BaseModel
from datetime import datetime
from typing import Optional

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