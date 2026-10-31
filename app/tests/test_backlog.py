def test_crud_backlog(client, admin, membro):
    criado = client.post(
        "/api/backlog/",
        headers=membro["headers"],
        json={
            "titulo": "Corrigir login",
            "descricao": "Ajustar validação de senha",
            "tipo": "BUG",
            "prioridade": "ALTA",
        },
    )
    assert criado.status_code == 201, criado.text
    item = criado.json()
    assert item["status"] == "PENDENTE"
    assert item["autor_id"] == membro["id"]

    listagem = client.get(
        "/api/backlog/?status=PENDENTE", headers=membro["headers"]
    )
    assert listagem.status_code == 200
    assert listagem.json()["total"] >= 1

    busca = client.get("/api/backlog/?busca=login", headers=membro["headers"])
    assert busca.status_code == 200
    assert busca.json()["total"] >= 1

    status = client.patch(
        f"/api/backlog/{item['id']}/status",
        headers=membro["headers"],
        json={"status": "EM_ANDAMENTO"},
    )
    assert status.status_code == 200
    assert status.json()["status"] == "EM_ANDAMENTO"

    atualizado = client.patch(
        f"/api/backlog/{item['id']}",
        headers=membro["headers"],
        json={"prioridade": "MEDIA"},
    )
    assert atualizado.status_code == 200
    assert atualizado.json()["prioridade"] == "MEDIA"

    admin_atualiza = client.patch(
        f"/api/backlog/{item['id']}",
        headers=admin["headers"],
        json={"titulo": "Alterado pelo administrador"},
    )
    assert admin_atualiza.status_code == 200

    do_admin = client.post(
        "/api/backlog/",
        headers=admin["headers"],
        json={"titulo": "Item do administrador", "tipo": "MELHORIA"},
    )
    assert do_admin.status_code == 201

    proibido = client.patch(
        f"/api/backlog/{do_admin.json()['id']}",
        headers=membro["headers"],
        json={"titulo": "Tentativa indevida"},
    )
    assert proibido.status_code == 403

    client.delete(f"/api/backlog/{do_admin.json()['id']}", headers=admin["headers"])

    removido = client.delete(
        f"/api/backlog/{item['id']}", headers=admin["headers"]
    )
    assert removido.status_code == 200

    inexistente = client.get(
        f"/api/backlog/{item['id']}", headers=admin["headers"]
    )
    assert inexistente.status_code == 404


def test_validacao_backlog(client, membro):
    resposta = client.post(
        "/api/backlog/",
        headers=membro["headers"],
        json={"titulo": "ab", "tipo": "INVALIDO"},
    )
    assert resposta.status_code == 422
