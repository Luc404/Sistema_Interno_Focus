"""Schemas Pydantic de notebooks (anotações pessoais).

Modela a criação, a resposta e a atualização parcial de notas, que são
organizadas por grupo e podem conter subtítulo, conteúdo e tags.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.schemas.partial import PartialUpdate


class NotebookCreate(BaseModel):
    """Payload de entrada para criação de uma nota."""

    # Grupo/caderno ao qual a nota pertence; padrão "PERSONAL NOTES".
    grupo: str = Field(default="PERSONAL NOTES", max_length=80)
    # Título da nota, entre 2 e 150 caracteres.
    titulo: str = Field(min_length=2, max_length=150)
    # Subtítulo opcional, até 255 caracteres.
    subtitulo: Optional[str] = Field(default=None, max_length=255)
    # Conteúdo da nota (obrigatório, ao menos 1 caractere).
    conteudo: str = Field(min_length=1)
    # Tags separadas por texto (ex.: "ideia,projeto"), opcional.
    tags: Optional[str] = Field(default=None, max_length=255)


class NotebookResponse(BaseModel):
    """Modelo de saída com os dados de uma nota."""

    id: int
    grupo: str
    titulo: str
    subtitulo: Optional[str] = None
    conteudo: str
    tags: Optional[str] = None
    # Data/hora de criação.
    data_criacao: datetime
    # Data/hora da última atualização.
    data_atualizacao: datetime
    # Usuário autor da nota.
    autor_id: int

    class Config:
        # Permite construir o schema a partir de objetos ORM.
        from_attributes = True


class NotebookUpdate(PartialUpdate):
    """Payload de atualização parcial de uma nota."""

    grupo: Optional[str] = Field(default=None, max_length=80)
    titulo: Optional[str] = Field(default=None, min_length=2, max_length=150)
    subtitulo: Optional[str] = Field(default=None, max_length=255)
    conteudo: Optional[str] = Field(default=None, min_length=1)
    tags: Optional[str] = Field(default=None, max_length=255)
