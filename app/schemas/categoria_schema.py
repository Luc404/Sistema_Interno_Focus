from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.schemas.partial import PartialUpdate


class CategoriaCreate(BaseModel):
    nome: str = Field(min_length=2, max_length=100)
    descricao: Optional[str] = Field(default=None, max_length=255)


class CategoriaResponse(BaseModel):
    id: int
    nome: str
    descricao: Optional[str] = None
    data_criacao: datetime

    class Config:
        from_attributes = True


class CategoriaUpdate(PartialUpdate):
    nome: Optional[str] = Field(default=None, min_length=2, max_length=100)
    descricao: Optional[str] = Field(default=None, max_length=255)


class PastaCreate(BaseModel):
    nome: str = Field(min_length=2, max_length=100)
    descricao: Optional[str] = Field(default=None, max_length=255)
    pasta_pai_id: Optional[int] = None


class PastaResponse(BaseModel):
    id: int
    nome: str
    descricao: Optional[str] = None
    pasta_pai_id: Optional[int] = None
    data_criacao: datetime

    class Config:
        from_attributes = True


class PastaUpdate(PartialUpdate):
    nome: Optional[str] = Field(default=None, min_length=2, max_length=100)
    descricao: Optional[str] = Field(default=None, max_length=255)
    pasta_pai_id: Optional[int] = None
