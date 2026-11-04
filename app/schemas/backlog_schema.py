"""Schemas Pydantic do backlog de demandas internas.

Define os tipos literais aceitos (status, prioridade e tipo), além dos
modelos de criação, resposta, atualização parcial e alteração apenas de
status de um item de backlog.
"""

from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field

from app.schemas.partial import PartialUpdate

# Valores permitidos para o status de um item do backlog.
StatusBacklog = Literal["PENDENTE", "EM_ANDAMENTO", "CONCLUIDO"]
# Valores permitidos para a prioridade do item.
PrioridadeBacklog = Literal["BAIXA", "MEDIA", "ALTA"]
# Valores permitidos para a classificação/tipo do item.
TipoBacklog = Literal["FEATURE", "BUG", "MELHORIA", "INFRA", "OUTRO"]


class BacklogCreate(BaseModel):
    """Payload de entrada para criação de um item de backlog."""

    # Título do item, entre 3 e 150 caracteres.
    titulo: str = Field(min_length=3, max_length=150)
    # Descrição detalhada opcional, até 500 caracteres.
    descricao: Optional[str] = Field(default=None, max_length=500)
    # Tipo obrigatório, restrito aos valores de ``TipoBacklog``.
    tipo: TipoBacklog
    # Prioridade com padrão "MEDIA" quando não informada.
    prioridade: PrioridadeBacklog = "MEDIA"
    # Status inicial com padrão "PENDENTE".
    status: StatusBacklog = "PENDENTE"
    # Setor responsável (chave estrangeira); opcional.
    setor_id: Optional[int] = None


class BacklogResponse(BaseModel):
    """Modelo de saída com os dados de um item de backlog."""

    id: int
    titulo: str
    descricao: Optional[str] = None
    # Na resposta os literais são expostos como texto simples.
    tipo: str
    prioridade: str
    status: str
    # Data/hora de criação do registro.
    data_criacao: datetime
    setor_id: Optional[int] = None
    # Usuário que criou o item (obrigatório na resposta).
    autor_id: int

    class Config:
        # Permite montar o schema a partir de instâncias ORM.
        from_attributes = True


class BacklogUpdate(PartialUpdate):
    """Payload de atualização parcial de um item de backlog.

    Todos os campos são opcionais; a exigência de ao menos um campo é
    herdada de ``PartialUpdate``.
    """

    titulo: Optional[str] = Field(default=None, min_length=3, max_length=150)
    descricao: Optional[str] = Field(default=None, max_length=500)
    tipo: Optional[TipoBacklog] = None
    prioridade: Optional[PrioridadeBacklog] = None
    status: Optional[StatusBacklog] = None
    setor_id: Optional[int] = None


class BacklogStatusUpdate(BaseModel):
    """Payload dedicado a alterar somente o status de um item."""

    # Novo status, restrito aos valores permitidos.
    status: StatusBacklog
