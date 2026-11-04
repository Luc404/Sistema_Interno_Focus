"""Testes de usuários e setores.

Cobre o CRUD de setores, restrições de permissão (membro não cria setor nem
lista usuários), atualização/desativação/reativação de usuários pelo admin e
validação de e-mail duplicado.
"""


def test_crud_setor(client, admin):
    """Valida o CRUD completo de setores pelo administrador.

    Cenário: cria um setor, tenta duplicar o nome, lista, atualiza a descrição
    e remove. Esperado: 201 na criação, 409 na duplicidade, listagem em 200,
    edição aplicada e exclusão em 200.
    """
    criado = client.post(
        "/api/setores/",
        headers=admin["headers"],
        json={"nome": "Desenvolvimento", "descricao": "Equipe de dev"},
    )
    assert criado.status_code == 201, criado.text
    setor = criado.json()

    # O nome do setor é único: duplicar deve gerar conflito (409).
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
    """Garante que membros não podem criar setores.

    Cenário: o membro tenta criar um setor. Esperado: 403.
    """
    resposta = client.post(
        "/api/setores/",
        headers=membro["headers"],
        json={"nome": "Financeiro"},
    )
    assert resposta.status_code == 403


def test_membro_nao_pode_listar_usuarios(client, membro):
    """Garante que membros não podem listar todos os usuários.

    Cenário: o membro acessa a listagem de usuários. Esperado: 403.
    """
    resposta = client.get("/api/usuarios/", headers=membro["headers"])
    assert resposta.status_code == 403


def test_admin_pode_atualizar_e_desativar_usuario(client, admin):
    """Valida atualização e alternância de ativação de um usuário pelo admin.

    Cenário: o admin cria um colaborador, atualiza o cargo, desativa e depois
    reativa o usuário. Esperado: cargo atualizado, ``ativo`` mudando para False
    e voltando para True, com todas as requisições em 200.
    """
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

    # Desativação lógica: o registro permanece, mas deixa de ficar ativo.
    desativado = client.post(
        f"/api/usuarios/{usuario['id']}/desativar",
        headers=admin["headers"],
    )
    assert desativado.status_code == 200
    assert desativado.json()["ativo"] is False

    # Reativação do mesmo usuário.
    reativado = client.post(
        f"/api/usuarios/{usuario['id']}/ativar",
        headers=admin["headers"],
    )
    assert reativado.status_code == 200
    assert reativado.json()["ativo"] is True


def test_email_duplicado(client, admin):
    """Valida a unicidade de e-mail no cadastro de usuários.

    Cenário: o admin tenta criar um usuário reutilizando o e-mail do admin.
    Esperado: 409 (conflito).
    """
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
