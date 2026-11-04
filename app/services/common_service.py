"""Utilitários compartilhados de paginação.

Fornece funções genéricas para contar e recortar consultas SQLAlchemy e montar
o schema padrão de página usado pelos demais serviços.
"""

from typing import Any

from sqlalchemy.orm import Query

from app.schemas.common import Page


def paginar(query: Query, skip: int, limit: int) -> tuple[list[Any], int]:
    """Executa uma consulta paginada retornando itens e total.

    Args:
        query: Consulta SQLAlchemy já filtrada e ordenada.
        skip: Quantidade de registros a ignorar (offset).
        limit: Quantidade máxima de registros a retornar.

    Returns:
        Uma tupla ``(items, total)`` onde ``items`` é a lista de registros da
        página atual e ``total`` é a contagem total sem paginação.

    Raises:
        Erros de banco são propagados pelo SQLAlchemy.
    """
    # count() considera os filtros aplicados, mas ignora offset/limit.
    total = query.count()
    # offset/limit recortam a janela de resultados pedida.
    items = query.offset(skip).limit(limit).all()
    return items, total


def montar_pagina(items: list[Any], total: int, skip: int, limit: int) -> Page:
    """Monta o schema de página a partir dos itens e metadados de paginação.

    Args:
        items: Registros da página atual.
        total: Total de registros que atendem aos filtros.
        skip: Offset aplicado.
        limit: Limite aplicado.

    Returns:
        Um schema ``Page`` preenchido.

    Raises:
        Erros de validação do schema são propagados.
    """
    return Page(items=items, total=total, skip=skip, limit=limit)
