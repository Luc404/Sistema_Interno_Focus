def test_crud_setor(client, admin):
    criado = client.post(
        "/api/setores/",
        headers=admin["headers"],
        json={"nome": "Desenvolvimento", "descricao": "Equipe de dev"},
    )
    assert criado.status_code == 201, criado.text
    setor = criado.json()

    duplicado = client.post(
        "/api/setores/",
        headers=admin["headers"],
        json={"nome": "Desenvolvimento"},
    )
    assert duplicado.status_code == 409

    listagem = client.get("/api/setores/", headers=admin["headers"])
    assert listagem.status_code == 200
    assert listagem.json()["total"] >= 1

    atualizado = client.patch(
        f"/api/setores/{setor['id']}",
        headers=admin["headers"],
        json={"descricao": "Equipe de desenvolvimento"},
    )
    assert atualizado.status_code == 200
    assert atualizado.json()["descricao"] == "Equipe de desenvolvimento"

    removido = client.delete(
        f"/api/setores/{setor['id']}", headers=admin["headers"]
    )
    assert removido.status_code == 200


def test_membro_nao_pode_criar_setor(client, membro):
    resposta = client.post(
        "/api/setores/",
        headers=membro["headers"],
        json={"nome": "Financeiro"},
    )
    assert resposta.status_code == 403


def test_membro_nao_pode_listar_usuarios(client, membro):
    resposta = client.get("/api/usuarios/", headers=membro["headers"])
    assert resposta.status_code == 403


def test_admin_pode_atualizar_e_desativar_usuario(client, admin):
    criado = client.post(
        "/api/usuarios/",
        headers=admin["headers"],
        json={
            "nome_completo": "Colaborador Temporario",
            "email": "temporario@example.com",
            "senha": "Senha123",
        },
    )
    assert criado.status_code == 201, criado.text
    usuario = criado.json()

    atualizado = client.patch(
        f"/api/usuarios/{usuario['id']}",
        headers=admin["headers"],
        json={"cargo": "Analista"},
    )
    assert atualizado.status_code == 200
    assert atualizado.json()["cargo"] == "Analista"

    desativado = client.post(
        f"/api/usuarios/{usuario['id']}/desativar",
        headers=admin["headers"],
    )
    assert desativado.status_code == 200
    assert desativado.json()["ativo"] is False

    reativado = client.post(
        f"/api/usuarios/{usuario['id']}/ativar",
        headers=admin["headers"],
    )
    assert reativado.status_code == 200
    assert reativado.json()["ativo"] is True


def test_email_duplicado(client, admin):
    resposta = client.post(
        "/api/usuarios/",
        headers=admin["headers"],
        json={
            "nome_completo": "Duplicado",
            "email": "admin@example.com",
            "senha": "Senha123",
        },
    )
    assert resposta.status_code == 409
