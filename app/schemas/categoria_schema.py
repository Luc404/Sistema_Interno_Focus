"""Schemas Pydantic de categorias e pastas de arquivos.

Categorias classificam arquivos por assunto, enquanto pastas permitem
organizá-los hierarquicamente (uma pasta pode ter uma pasta "pai").
Este módulo cobre criação, resposta e atualização parcial de ambos.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.schemas.partial import PartialUpdate


class CategoriaCreate(BaseModel):
    """Payload de entrada para criação de uma categoria."""

    # Nome da categoria, entre 2 e 100 caracteres.
    nome: str = Field(min_length=2, max_length=100)
    # Descrição opcional, até 255 caracteres.
    descricao: Optional[str] = Field(default=None, max_length=255)


class CategoriaResponse(BaseModel):
    """Modelo de saída com os dados de uma categoria."""

    id: int
    nome: str
    descricao: Optional[str] = None
    # Data/hora de criação do registro.
    data_criacao: datetime

    class Config:
        # Permite construir o schema a partir de objetos ORM.
        from_attributes = True


class CategoriaUpdate(PartialUpdate):
    """Payload de atualização parcial de uma categoria.

    Campos opcionais; ao menos um deve ser enviado (regra de
    ``PartialUpdate``).
    """

    nome: Optional[str] = Field(default=None, min_length=2, max_length=100)
    descricao: Optional[str] = Field(default=None, max_length=255)


class PastaCreate(BaseModel):
    """Payload de entrada para criação de uma pasta de arquivos."""

    nome: str = Field(min_length=2, max_length=100)
    descricao: Optional[str] = Field(default=None, max_length=255)
    # Referência à pasta superior na hierarquia; ``None`` indica raiz.
    pasta_pai_id: Optional[int] = None


class PastaResponse(BaseModel):
    """Modelo de saída com os dados de uma pasta."""

    id: int
    nome: str
    descricao: Optional[str] = None
    # Pasta "pai" referenciada (None para pastas raiz).
    pasta_pai_id: Optional[int] = None
    data_criacao: datetime

    class Config:
        # Permite construir o schema a partir de objetos ORM.
        from_attributes = True


class PastaUpdate(PartialUpdate):
    """Payload de atualização parcial de uma pasta."""

    nome: Optional[str] = Field(default=None, min_length=2, max_length=100)
    descricao: Optional[str] = Field(default=None, max_length=255)
    # Permite mover a pasta para outra pasta pai (ou para a raiz com None).
    pasta_pai_id: Optional[int] = None
