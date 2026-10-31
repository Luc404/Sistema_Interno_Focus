from typing import Any, TypeVar

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.model.setor import Setor
from app.model.usuario import Usuario

ModelT = TypeVar("ModelT")


def obter_ou_404(db: Session, model: type[ModelT], obj_id: int, nome: str = "Registro") -> ModelT:
    obj = db.get(model, obj_id)
    if not obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{nome} não encontrado(a)",
        )
    return obj


def validar_setor(db: Session, setor_id: int | None) -> Setor | None:
    if setor_id is None:
        return None
    return obter_ou_404(db, Setor, setor_id, "Setor")


def validar_usuario(db: Session, usuario_id: int | None) -> Usuario | None:
    if usuario_id is None:
        return None
    return obter_ou_404(db, Usuario, usuario_id, "Usuário")


def aplicar_atualizacao(obj: Any, dados: dict[str, Any]) -> None:
    for campo, valor in dados.items():
        setattr(obj, campo, valor)
