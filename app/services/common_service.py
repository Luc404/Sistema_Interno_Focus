from typing import Any

from sqlalchemy.orm import Query

from app.schemas.common import Page


def paginar(query: Query, skip: int, limit: int) -> tuple[list[Any], int]:
    total = query.count()
    items = query.offset(skip).limit(limit).all()
    return items, total


def montar_pagina(items: list[Any], total: int, skip: int, limit: int) -> Page:
    return Page(items=items, total=total, skip=skip, limit=limit)
