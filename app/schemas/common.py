"""Schemas genéricos reutilizados em toda a API.

Fornece um envelope de paginação (``Page``) parametrizável por qualquer
tipo de item e um modelo simples de mensagem de retorno (``Mensagem``).
"""

from typing import Generic, TypeVar

from pydantic import BaseModel

# Tipo genérico que representa o elemento contido na página.
T = TypeVar("T")


class Page(BaseModel, Generic[T]):
    """Envelope genérico de resposta paginada.

    ``Generic[T]`` permite especializar a página para qualquer schema,
    por exemplo ``Page[UsuarioResponse]``, mantendo a validação de tipos.
    """

    # Itens da página atual.
    items: list[T]
    # Total de registros existentes (antes da paginação).
    total: int
    # Quantidade de registros ignorados no início (offset).
    skip: int
    # Quantidade máxima de registros retornados.
    limit: int


class Mensagem(BaseModel):
    """Resposta simples contendo uma mensagem textual."""

    # Texto a ser exibido ao cliente.
    mensagem: str
