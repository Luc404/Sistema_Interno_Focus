"""Schemas Pydantic de tarefas pessoais.

Modela a criação, a resposta, a atualização parcial e a alteração de
status de tarefas pertencentes a um usuário.
"""

from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field

from app.schemas.partial import PartialUpdate

# Situações possíveis de uma tarefa pessoal.
StatusTarefa = Literal["PENDENTE", "EM_ANDAMENTO", "CONCLUIDA"]


class TarefaPessoalCreate(BaseModel):
    """Payload de entrada para criação de uma tarefa pessoal."""

    # Título, entre 3 e 150 caracteres.
    titulo: str = Field(min_length=3, max_length=150)
    # Descrição opcional, até 500 caracteres.
    descricao: Optional[str] = Field(default=None, max_length=500)
    # Prazo/limite opcional para conclusão.
    data_limite: Optional[datetime] = None
    # Status inicial; padrão "PENDENTE".
    status: StatusTarefa = "PENDENTE"


class TarefaPessoalResponse(BaseModel):
    """Modelo de saída com os dados de uma tarefa pessoal."""

    id: int
    titulo: str
    descricao: Optional[str] = None
    data_limite: Optional[datetime] = None
    status: StatusTarefa
    # Usuário dono da tarefa.
    usuario_id: int

    class Config:
        # Permite construir o schema a partir de objetos ORM.
        from_attributes = True


class TarefaPessoalUpdate(PartialUpdate):
    """Payload de atualização parcial de uma tarefa pessoal."""

    titulo: Optional[str] = Field(default=None, min_length=3, max_length=150)
    descricao: Optional[str] = Field(default=None, max_length=500)
    data_limite: Optional[datetime] = None
    status: Optional[StatusTarefa] = None


class TarefaStatusUpdate(BaseModel):
    """Payload dedicado a alterar somente o status de uma tarefa."""

    # Novo status, restrito aos valores permitidos.
    status: StatusTarefa
