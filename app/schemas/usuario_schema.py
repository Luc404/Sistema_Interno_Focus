"""Schemas Pydantic de usuários.

Define os perfis aceitos e os modelos de usuário para criação, resposta,
versão resumida (usada em relacionamentos), atualização administrativa e
autoedição de perfil. Inclui a validação de força mínima da senha.
"""

from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.schemas.partial import PartialUpdate

# Perfis de acesso possíveis: administrador ou membro comum.
Perfil = Literal["ADMIN", "MEMBRO"]


class UsuarioBase(BaseModel):
    """Campos comuns de um usuário, reaproveitados na criação."""

    # Nome completo, entre 2 e 150 caracteres.
    nome_completo: str = Field(min_length=2, max_length=150)
    # E-mail validado quanto ao formato.
    email: EmailStr
    # Cargo/função opcional, até 100 caracteres.
    cargo: Optional[str] = Field(default=None, max_length=100)
    # Perfil de acesso; padrão "MEMBRO".
    perfil: Perfil = "MEMBRO"
    # Setor ao qual o usuário pertence (chave estrangeira); opcional.
    setor_id: Optional[int] = None


class UsuarioCreate(UsuarioBase):
    """Payload de entrada para criação de um usuário.

    Herda todos os campos de ``UsuarioBase`` e adiciona a senha.
    """

    # Senha, entre 8 e 128 caracteres (validada pelo método abaixo).
    senha: str = Field(min_length=8, max_length=128)

    @field_validator("senha")
    @classmethod
    def senha_forte(cls, valor: str) -> str:
        """Exige que a senha tenha ao menos uma letra e um número.

        A validação roda após a checagem de tamanho do ``Field`` e rejeita
        senhas puramente alfabéticas ou puramente numéricas.
        """
        # ``isdigit``/``isalpha`` verificam a presença de dígitos e letras.
        if not any(c.isdigit() for c in valor) or not any(c.isalpha() for c in valor):
            raise ValueError("A senha deve conter letras e números")
        return valor


class UsuarioResponse(BaseModel):
    """Modelo de saída com os dados de um usuário."""

    id: int
    nome_completo: str
    email: EmailStr
    cargo: Optional[str] = None
    perfil: Perfil
    # Indica se o usuário está ativo no sistema.
    ativo: bool
    # Data/hora de cadastro.
    data_cadastro: datetime
    setor_id: Optional[int] = None

    class Config:
        # Permite construir o schema a partir de objetos ORM.
        from_attributes = True


class UsuarioResumo(BaseModel):
    """Versão resumida de usuário, usada em relacionamentos.

    Ex.: participantes de reuniões, autores de registros. Contém apenas
    os dados básicos necessários para identificação.
    """

    id: int
    nome_completo: str
    email: EmailStr
    perfil: Perfil

    class Config:
        # Permite construir o schema a partir de objetos ORM.
        from_attributes = True


class UsuarioUpdate(PartialUpdate):
    """Payload de atualização parcial de usuário (visão administrativa).

    Permite alterar também ``perfil`` e ``ativo``, além dos dados básicos.
    """

    nome_completo: Optional[str] = Field(default=None, min_length=2, max_length=150)
    email: Optional[EmailStr] = None
    cargo: Optional[str] = Field(default=None, max_length=100)
    perfil: Optional[Perfil] = None
    setor_id: Optional[int] = None
    # Permite ativar/desativar o usuário.
    ativo: Optional[bool] = None


class UsuarioSelfUpdate(PartialUpdate):
    """Payload de autoedição de perfil.

    Restringe os campos que o próprio usuário pode alterar: apenas nome e
    cargo. Campos sensíveis (perfil, ativo, setor) ficam fora deste schema.
    """

    nome_completo: Optional[str] = Field(default=None, min_length=2, max_length=150)
    cargo: Optional[str] = Field(default=None, max_length=100)
