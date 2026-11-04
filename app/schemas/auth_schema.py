"""Schemas Pydantic de autenticação.

Agrupa os payloads de login, emissão/refresh de tokens JWT e troca de
senha. São usados pelos endpoints de autenticação para validar as
requisições e padronizar as respostas.
"""

from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    """Credenciais enviadas pelo usuário no login."""

    # E-mail validado quanto ao formato (EmailStr).
    email: EmailStr
    # Senha em texto puro, validada posteriormente na camada de serviço.
    senha: str


class Token(BaseModel):
    """Resposta padrão de autenticação bem-sucedida com os tokens emitidos."""

    # Token de acesso de curta duração usado nas requisições autenticadas.
    access_token: str
    # Token usado para renovar o access_token sem novo login.
    refresh_token: str
    # Esquema do token; por padrão "bearer" (OAuth2).
    token_type: str = "bearer"
    # Tempo de validade do access_token, em segundos.
    expires_in: int


class RefreshRequest(BaseModel):
    """Payload para renovar o token de acesso a partir do refresh token."""

    # Refresh token previamente emitido no login.
    refresh_token: str


class AlterarSenhaRequest(BaseModel):
    """Payload para troca de senha de um usuário autenticado."""

    # Senha atual, usada para confirmar a identidade antes da troca.
    senha_atual: str
    # Nova senha, exigindo entre 8 e 128 caracteres.
    nova_senha: str = Field(min_length=8, max_length=128)
