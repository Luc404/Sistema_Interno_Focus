"""Validadores e utilitários de persistência reutilizáveis.

Auxilia na busca de registros com erro 404, na validação de setores e
usuários e na aplicação parcial de atualizações em modelos.
"""

from typing import Any, TypeVar

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.model.setor import Setor
from app.model.usuario import Usuario

ModelT = TypeVar("ModelT")


def obter_ou_404(db: Session, model: type[ModelT], obj_id: int, nome: str = "Registro") -> ModelT:
    """Busca um registro pelo id e levanta HTTP 404 quando ele não existe."""
    obj = db.get(model, obj_id)
    if not obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{nome} não encontrado(a)",
        )
    return obj


def validar_setor(db: Session, setor_id: int | None) -> Setor | None:
    """Retorna o setor correspondente ou None quando o id não é informado."""
    if setor_id is None:
        return None
    return obter_ou_404(db, Setor, setor_id, "Setor")


def validar_usuario(db: Session, usuario_id: int | None) -> Usuario | None:
    """Retorna o usuário correspondente ou None quando o id não é informado."""
    if usuario_id is None:
        return None
    return obter_ou_404(db, Usuario, usuario_id, "Usuário")


def aplicar_atualizacao(obj: Any, dados: dict[str, Any]) -> None:
    """Atribui dinamicamente os campos informados ao objeto."""
    for campo, valor in dados.items():
        setattr(obj, campo, valor)
