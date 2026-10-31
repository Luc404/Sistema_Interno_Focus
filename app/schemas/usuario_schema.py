from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.schemas.partial import PartialUpdate

Perfil = Literal["ADMIN", "MEMBRO"]


class UsuarioBase(BaseModel):
    nome_completo: str = Field(min_length=2, max_length=150)
    email: EmailStr
    cargo: Optional[str] = Field(default=None, max_length=100)
    perfil: Perfil = "MEMBRO"
    setor_id: Optional[int] = None


class UsuarioCreate(UsuarioBase):
    senha: str = Field(min_length=8, max_length=128)

    @field_validator("senha")
    @classmethod
    def senha_forte(cls, valor: str) -> str:
        if not any(c.isdigit() for c in valor) or not any(c.isalpha() for c in valor):
            raise ValueError("A senha deve conter letras e números")
        return valor


class UsuarioResponse(BaseModel):
    id: int
    nome_completo: str
    email: EmailStr
    cargo: Optional[str] = None
    perfil: Perfil
    ativo: bool
    data_cadastro: datetime
    setor_id: Optional[int] = None

    class Config:
        from_attributes = True


class UsuarioResumo(BaseModel):
    id: int
    nome_completo: str
    email: EmailStr
    perfil: Perfil

    class Config:
        from_attributes = True


class UsuarioUpdate(PartialUpdate):
    nome_completo: Optional[str] = Field(default=None, min_length=2, max_length=150)
    email: Optional[EmailStr] = None
    cargo: Optional[str] = Field(default=None, max_length=100)
    perfil: Optional[Perfil] = None
    setor_id: Optional[int] = None
    ativo: Optional[bool] = None


class UsuarioSelfUpdate(PartialUpdate):
    nome_completo: Optional[str] = Field(default=None, min_length=2, max_length=150)
    cargo: Optional[str] = Field(default=None, max_length=100)
