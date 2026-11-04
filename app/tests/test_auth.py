"""Testes de autenticação e autorização básica.

Cobre o healthcheck, a proteção de rotas sem token, login inválido, consulta do
próprio perfil, renovação de token, bloqueio do registro público quando já há
usuários e a troca de senha autenticada.
"""


def test_health(client):
    """Verifica o endpoint de saúde da aplicação.

    Cenário: consulta ``/health`` sem autenticação. Esperado: 200 e banco "ok".
    """
    resposta = client.get("/health")
    assert resposta.status_code == 200
    assert resposta.json()["banco"] == "ok"


def test_rota_protegida_sem_token(client):
    """Garante que rotas protegidas rejeitam requisições sem token.

    Cenário: acessa a listagem de usuários sem cabeçalho de autorização.
    Esperado: 401 (não autenticado).
    """
    resposta = client.get("/api/usuarios/")
    assert resposta.status_code == 401


def test_login_invalido(client):
    """Valida a rejeição de login com credenciais inexistentes.

    Cenário: tenta autenticar com e-mail que não existe. Esperado: 401.
    """
    resposta = client.post(
        "/api/auth/login",
        json={"email": "ninguem@example.com", "senha": "Senha123"},
    )
    assert resposta.status_code == 401


def test_me(client, admin):
    """Confirma que ``/auth/me`` retorna os dados do usuário autenticado.

    Cenário: admin consulta o próprio perfil. Esperado: 200 com e-mail e perfil
    correspondentes ao usuário criado pela fixture.
    """
    resposta = client.get("/api/auth/me", headers=admin["headers"])
    assert resposta.status_code == 200
    assert resposta.json()["email"] == "admin@example.com"
    assert resposta.json()["perfil"] == "ADMIN"


def test_refresh_token(client, admin):
    """Valida a emissão de um novo access token via refresh token.

    Cenário: envia o refresh token obtido no login do admin. Esperado: 200 com
    um ``access_token`` válido no corpo.
    """
    resposta = client.post(
        "/api/auth/refresh",
        json={"refresh_token": admin["tokens"]["refresh_token"]},
    )
    assert resposta.status_code == 200
    assert resposta.json()["access_token"]


def test_registro_publico_bloqueado_com_usuarios_existentes(client):
    """Impede cadastros públicos quando já existem usuários no sistema.

    Cenário: tenta registrar um novo usuário pela rota pública após o admin já
    ter sido criado. Esperado: 403 (registro público desabilitado).
    """
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
    """Valida a troca de senha e a restauração ao valor original.

    Cenário: o membro troca a senha, faz login com a nova e depois restaura a
    senha antiga para não afetar os demais testes. Esperado: todas as operações
    em 200 e login funcionando com a nova senha.
    """
    resposta = client.post(
        "/api/auth/alterar-senha",
        headers=membro["headers"],
        json={"senha_atual": "Senha123", "nova_senha": "NovaSenha123"},
    )
    assert resposta.status_code == 200

    # Confirma que a nova senha é aceita no login.
    login = client.post(
        "/api/auth/login",
        json={"email": "membro@example.com", "senha": "NovaSenha123"},
    )
    assert login.status_code == 200

    # Restaura a senha original para manter a fixture consistente.
    restaurar = client.post(
        "/api/auth/alterar-senha",
        headers=membro["headers"],
        json={"senha_atual": "NovaSenha123", "nova_senha": "Senha123"},
    )
    assert restaurar.status_code == 200
