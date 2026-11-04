"""Configurações centralizadas da aplicação.

Define os parâmetros lidos de variáveis de ambiente e do arquivo .env,
incluindo banco de dados, autenticação, CORS e uploads.
"""

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Agrupa todas as configurações da API carregadas do ambiente."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "Sistema Focus API"
    app_version: str = "1.0.0"
    environment: str = "development"
    debug: bool = False
    api_prefix: str = "/api"

    database_url: str = "postgresql://postgres:postgres@localhost:5432/sistema_focus_db"

    # Parâmetros usados na geração e validação dos tokens JWT.
    secret_key: str = "troque-esta-chave-em-producao"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    refresh_token_expire_days: int = 7

    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    # Diretório e limite de tamanho para arquivos enviados.
    upload_dir: str = "uploads"
    max_upload_size_mb: int = 25

    auto_create_tables: bool = True

    # Dados do administrador inicial criado na primeira execução.
    first_admin_email: str = ""
    first_admin_password: str = ""
    first_admin_nome: str = "Administrador"

    @property
    def cors_origins_list(self) -> list[str]:
        """Retorna as origens de CORS como uma lista, removendo espaços vazios."""
        return [origem.strip() for origem in self.cors_origins.split(",") if origem.strip()]

    @property
    def max_upload_size_bytes(self) -> int:
        """Converte o limite de upload de megabytes para bytes."""
        return self.max_upload_size_mb * 1024 * 1024

    @property
    def upload_path(self) -> Path:
        """Retorna o diretório de upload, criando-o caso ainda não exista."""
        caminho = Path(self.upload_dir)
        caminho.mkdir(parents=True, exist_ok=True)
        return caminho


@lru_cache
def get_settings() -> Settings:
    """Retorna uma instância única e em cache das configurações."""
    return Settings()
