"""Schemas Pydantic relacionados a arquivos do sistema.

Define os modelos de entrada (criação), saída (resposta) e atualização
parcial de arquivos, incluindo metadados como tipo MIME, caminho de
armazenamento, tamanho e vínculos com categoria, pasta e usuário.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.schemas.partial import PartialUpdate


class ArquivoCreate(BaseModel):
    """Payload de entrada para cadastro de um novo arquivo."""

    # Título exibido do arquivo. Obrigatório, entre 1 e 100 caracteres.
    titulo: str = Field(min_length=1, max_length=100)
    # Nome/descrição textual da categoria; opcional.
    categoria: Optional[str] = Field(default=None, max_length=100)
    # Referência à categoria persistida (chave estrangeira); opcional.
    categoria_id: Optional[int] = None
    # Referência à pasta onde o arquivo está organizado; opcional.
    pasta_id: Optional[int] = None
    # Tipo MIME do arquivo (ex.: "application/pdf"); obrigatório.
    tipo_mime: str = Field(max_length=100)
    # Caminho/local de armazenamento do arquivo; obrigatório.
    caminho_arquivo: str = Field(max_length=500)
    # Tamanho em bytes; não pode ser negativo (ge=0).
    tamanho_bytes: int = Field(ge=0)
    # Usuário responsável pelo upload; opcional na entrada.
    usuario_id: Optional[int] = None


class ArquivoResponse(BaseModel):
    """Modelo de saída com os dados completos de um arquivo."""

    # Identificador gerado pelo banco.
    id: int
    titulo: str
    caminho_arquivo: str
    tipo_mime: str
    # Campos opcionais podem vir nulos.
    categoria: Optional[str] = None
    categoria_id: Optional[int] = None
    pasta_id: Optional[int] = None
    tamanho_bytes: int
    # Data/hora em que o upload foi realizado.
    data_upload: datetime
    # Usuário que fez o upload (obrigatório na resposta).
    usuario_id: int

    class Config:
        # Permite construir o schema diretamente a partir de objetos ORM
        # (atributos lidos via getattr), em vez de apenas dicionários.
        from_attributes = True


class ArquivoUpdate(PartialUpdate):
    """Payload de atualização parcial de um arquivo.

    Todos os campos são opcionais para que apenas o que foi enviado seja
    alterado; a validação de "ao menos um campo" vem de ``PartialUpdate``.
    """

    titulo: Optional[str] = Field(default=None, min_length=1, max_length=100)
    categoria: Optional[str] = Field(default=None, max_length=100)
    categoria_id: Optional[int] = None
    pasta_id: Optional[int] = None
