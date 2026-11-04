"""Configuração compartilhada dos testes (fixtures do pytest).

Este módulo define o ambiente de execução dos testes antes de importar a
aplicação: aponta o banco para um arquivo SQLite temporário, desabilita a
criação automática de tabelas, define uma chave secreta de teste e um diretório
temporário para uploads. Também expõe fixtures reutilizáveis que criam o
cliente HTTP da API e os usuários ``admin`` e ``membro`` já autenticados.
"""

import os
import tempfile
from pathlib import Path

# Banco de teste isolado em um arquivo dentro do diretório temporário do SO.
# A remoção prévia (missing_ok=True) garante que cada execução comece limpa.
TEST_DB = Path(tempfile.gettempdir()) / "focus_backend_test.db"
TEST_DB.unlink(missing_ok=True)

# Variáveis de ambiente precisam ser definidas ANTES de importar app.database e
# app.main, pois as configurações são lidas no momento do import dos módulos.
os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DB}"
# Os testes controlam o schema manualmente (drop/create), então não deixamos a
# aplicação criar tabelas no startup.
os.environ["AUTO_CREATE_TABLES"] = "false"
os.environ["SECRET_KEY"] = "chave-de-teste-com-mais-de-32-caracteres"
# Diretório temporário exclusivo para os uploads realizados nos testes.
os.environ["UPLOAD_DIR"] = tempfile.mkdtemp(prefix="focus_uploads_")
# Desabilita a criação automática do admin inicial; a fixture "admin" cuida disso.
os.environ["FIRST_ADMIN_EMAIL"] = ""
os.environ["FIRST_ADMIN_PASSWORD"] = ""
os.environ["CORS_ORIGINS"] = "http://localhost:5173"

import pytest
from fastapi.testclient import TestClient

from app.database import Base, engine
from app.main import app


@pytest.fixture(scope="session")
def client():
    """Fornece um cliente de testes da API com banco limpo por sessão.

    Antes dos testes, o schema é recriado do zero (drop + create). O cliente é
    aberto em um context manager para disparar os eventos de startup/shutdown
    (lifespan) da aplicação. Ao final, o schema é novamente descartado.
    """
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as test_client:
        yield test_client
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="session")
def admin(client):
    """Cria e autentica o usuário administrador usado na maioria dos testes.

    Registra o admin via endpoint público, faz login e devolve um dicionário com
    o id, e-mail, cabeçalhos de autorização (Bearer) e os tokens emitidos.
    """
    resposta = client.post(
        "/api/auth/registrar",
        json={
            "nome_completo": "Admin Teste",
            "email": "admin@example.com",
            "senha": "Senha123",
            "perfil": "ADMIN",
        },
    )
    assert resposta.status_code == 201, resposta.text
    usuario = resposta.json()

    # Login para obter o par de tokens (access e refresh).
    login = client.post(
        "/api/auth/login",
        json={"email": "admin@example.com", "senha": "Senha123"},
    )
    assert login.status_code == 200, login.text
    tokens = login.json()

    # Cabeçalho pronto para requisições autenticadas como admin.
    return {
        "id": usuario["id"],
        "email": usuario["email"],
        "headers": {"Authorization": f"Bearer {tokens['access_token']}"},
        "tokens": tokens,
    }


@pytest.fixture(scope="session")
def membro(client, admin):
    """Cria e autentica um usuário de perfil MEMBRO.

    Depende da fixture ``admin`` (usada como cabeçalho de autorização para o
    cadastro). Devolve id, e-mail, cabeçalhos e tokens do membro recém-criado.
    """
    resposta = client.post(
        "/api/usuarios/",
        headers=admin["headers"],
        json={
            "nome_completo": "Membro Teste",
            "email": "membro@example.com",
            "senha": "Senha123",
            "perfil": "MEMBRO",
        },
    )
    assert resposta.status_code == 201, resposta.text
    usuario = resposta.json()

    # Login do membro para obter os tokens de acesso.
    login = client.post(
        "/api/auth/login",
        json={"email": "membro@example.com", "senha": "Senha123"},
    )
    assert login.status_code == 200, login.text
    tokens = login.json()

    # Cabeçalho pronto para requisições autenticadas como membro.
    return {
        "id": usuario["id"],
        "email": usuario["email"],
        "headers": {"Authorization": f"Bearer {tokens['access_token']}"},
        "tokens": tokens,
    }
