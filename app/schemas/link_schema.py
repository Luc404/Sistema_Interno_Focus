"""Schemas Pydantic de links úteis.

Modela o cadastro, a resposta e a atualização parcial de links, com
validação de URL via ``HttpUrl`` e campos opcionais de descrição e
categoria.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, HttpUrl

from app.schemas.partial import PartialUpdate


class LinkCreate(BaseModel):
    """Payload de entrada para criação de um link."""

    # Título do link, entre 2 e 160 caracteres.
    titulo: str = Field(min_length=2, max_length=160)
    # URL validada quanto ao formato (deve ser HTTP/HTTPS).
    url: HttpUrl
    # Descrição opcional, até 255 caracteres.
    descricao: Optional[str] = Field(default=None, max_length=255)
    # Categoria textual opcional do link.
    categoria: Optional[str] = Field(default=None, max_length=100)


class LinkResponse(BaseModel):
    """Modelo de saída com os dados de um link."""

    id: int
    titulo: str
    # URL já validada e serializada.
    url: HttpUrl
    descricao: Optional[str] = None
    categoria: Optional[str] = None
    # Data/hora de criação do registro.
    data_criacao: datetime
    # Usuário que cadastrou o link.
    usuario_id: int

    class Config:
        # Permite construir o schema a partir de objetos ORM.
        from_attributes = True


class LinkUpdate(PartialUpdate):
    """Payload de atualização parcial de um link."""

    titulo: Optional[str] = Field(default=None, min_length=2, max_length=160)
    url: Optional[HttpUrl] = None
    descricao: Optional[str] = Field(default=None, max_length=255)
    categoria: Optional[str] = Field(default=None, max_length=100)
