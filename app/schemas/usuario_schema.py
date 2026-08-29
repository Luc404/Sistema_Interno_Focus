from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UsuarioCreate(BaseModel):
    nome_completo: str
    email: EmailStr
    senha: str
    cargo: Optional[str] = None
    perfil: Optional[str] = "MEMBRO"
    setor_id: Optional[int] = None

class UsuarioResponse(BaseModel):
    id: int
    nome_completo: str
    email: EmailStr
    cargo: Optional[str] = None
    perfil: Optional[str] = "MEMBRO"
    ativo: bool
    data_cadastro: datetime
    setor_id: Optional[int] = None

    class Config:
        from_attributes = True