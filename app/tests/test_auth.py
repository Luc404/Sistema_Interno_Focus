def test_health(client):
    resposta = client.get("/health")
    assert resposta.status_code == 200
    assert resposta.json()["banco"] == "ok"


def test_rota_protegida_sem_token(client):
    resposta = client.get("/api/usuarios/")
    assert resposta.status_code == 401


def test_login_invalido(client):
    resposta = client.post(
        "/api/auth/login",
        json={"email": "ninguem@example.com", "senha": "Senha123"},
    )
    assert resposta.status_code == 401


def test_me(client, admin):
    resposta = client.get("/api/auth/me", headers=admin["headers"])
    assert resposta.status_code == 200
    assert resposta.json()["email"] == "admin@example.com"
    assert resposta.json()["perfil"] == "ADMIN"


def test_refresh_token(client, admin):
    resposta = client.post(
        "/api/auth/refresh",
        json={"refresh_token": admin["tokens"]["refresh_token"]},
    )
    assert resposta.status_code == 200
    assert resposta.json()["access_token"]


def test_registro_publico_bloqueado_com_usuarios_existentes(client):
    resposta = client.post(
        "/api/auth/registrar",
        json={
            "nome_completo": "Intruso",
            "email": "intruso@example.com",
            "senha": "Senha123",
        },
    )
    assert resposta.status_code == 403


def test_alterar_senha(client, membro):
    resposta = client.post(
        "/api/auth/alterar-senha",
        headers=membro["headers"],
        json={"senha_atual": "Senha123", "nova_senha": "NovaSenha123"},
    )
    assert resposta.status_code == 200

    login = client.post(
        "/api/auth/login",
        json={"email": "membro@example.com", "senha": "NovaSenha123"},
    )
    assert login.status_code == 200

    restaurar = client.post(
        "/api/auth/alterar-senha",
        headers=membro["headers"],
        json={"senha_atual": "NovaSenha123", "nova_senha": "Senha123"},
    )
    assert restaurar.status_code == 200
