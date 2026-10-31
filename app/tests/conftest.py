import os
import tempfile
from pathlib import Path

TEST_DB = Path(tempfile.gettempdir()) / "focus_backend_test.db"
TEST_DB.unlink(missing_ok=True)

os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DB}"
os.environ["AUTO_CREATE_TABLES"] = "false"
os.environ["SECRET_KEY"] = "chave-de-teste-com-mais-de-32-caracteres"
os.environ["UPLOAD_DIR"] = tempfile.mkdtemp(prefix="focus_uploads_")
os.environ["FIRST_ADMIN_EMAIL"] = ""
os.environ["FIRST_ADMIN_PASSWORD"] = ""
os.environ["CORS_ORIGINS"] = "http://localhost:5173"

import pytest
from fastapi.testclient import TestClient

from app.database import Base, engine
from app.main import app


@pytest.fixture(scope="session")
def client():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as test_client:
        yield test_client
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="session")
def admin(client):
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

    login = client.post(
        "/api/auth/login",
        json={"email": "admin@example.com", "senha": "Senha123"},
    )
    assert login.status_code == 200, login.text
    tokens = login.json()

    return {
        "id": usuario["id"],
        "email": usuario["email"],
        "headers": {"Authorization": f"Bearer {tokens['access_token']}"},
        "tokens": tokens,
    }


@pytest.fixture(scope="session")
def membro(client, admin):
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

    login = client.post(
        "/api/auth/login",
        json={"email": "membro@example.com", "senha": "Senha123"},
    )
    assert login.status_code == 200, login.text
    tokens = login.json()

    return {
        "id": usuario["id"],
        "email": usuario["email"],
        "headers": {"Authorization": f"Bearer {tokens['access_token']}"},
        "tokens": tokens,
    }
