def test_crud_tarefa_pessoal(client, admin, membro):
    criada = client.post(
        "/api/tarefas-pessoais/",
        headers=membro["headers"],
        json={
            "titulo": "Revisar proposta",
            "descricao": "Conferir valores",
            "data_limite": "2030-01-10T18:00:00",
        },
    )
    assert criada.status_code == 201, criada.text
    tarefa = criada.json()
    assert tarefa["usuario_id"] == membro["id"]

    minhas = client.get(
        "/api/tarefas-pessoais/minhas", headers=membro["headers"]
    )
    assert minhas.status_code == 200
    assert minhas.json()["total"] >= 1

    do_usuario = client.get(
        f"/api/tarefas-pessoais/usuario/{membro['id']}",
        headers=admin["headers"],
    )
    assert do_usuario.status_code == 200

    status = client.patch(
        f"/api/tarefas-pessoais/{tarefa['id']}/status",
        headers=membro["headers"],
        json={"status": "CONCLUIDA"},
    )
    assert status.status_code == 200
    assert status.json()["status"] == "CONCLUIDA"

    removida = client.delete(
        f"/api/tarefas-pessoais/{tarefa['id']}", headers=membro["headers"]
    )
    assert removida.status_code == 200


def test_crud_link(client, membro):
    criado = client.post(
        "/api/links/",
        headers=membro["headers"],
        json={
            "titulo": "Documentação FastAPI",
            "url": "https://fastapi.tiangolo.com",
            "descricao": "Documentação oficial",
            "categoria": "Backend",
        },
    )
    assert criado.status_code == 201, criado.text
    link = criado.json()

    listagem = client.get("/api/links/?categoria=Backend", headers=membro["headers"])
    assert listagem.status_code == 200
    assert listagem.json()["total"] >= 1

    atualizado = client.patch(
        f"/api/links/{link['id']}",
        headers=membro["headers"],
        json={"descricao": "Docs atualizadas"},
    )
    assert atualizado.status_code == 200
    assert atualizado.json()["descricao"] == "Docs atualizadas"

    removido = client.delete(
        f"/api/links/{link['id']}", headers=membro["headers"]
    )
    assert removido.status_code == 200


def test_crud_reuniao_com_participantes(client, admin, membro):
    criada = client.post(
        "/api/reunioes/",
        headers=admin["headers"],
        json={
            "titulo": "Planejamento semanal",
            "descricao": "Alinhamento da equipe",
            "data_hora_inicio": "2030-02-01T10:00:00",
            "data_hora_fim": "2030-02-01T11:00:00",
            "link_reuniao": "https://meet.example.com/sala",
            "participantes_ids": [membro["id"]],
        },
    )
    assert criada.status_code == 201, criada.text
    reuniao = criada.json()
    assert len(reuniao["participantes"]) == 1
    assert reuniao["participantes"][0]["id"] == membro["id"]

    listagem = client.get("/api/reunioes/?busca=Planejamento", headers=membro["headers"])
    assert listagem.status_code == 200
    assert listagem.json()["total"] >= 1

    proximas = client.get("/api/reunioes/proximas", headers=membro["headers"])
    assert proximas.status_code == 200
    assert any(item["id"] == reuniao["id"] for item in proximas.json())

    participantes = client.get(
        f"/api/reunioes/{reuniao['id']}/participantes",
        headers=membro["headers"],
    )
    assert participantes.status_code == 200
    assert len(participantes.json()) == 1

    adicionado = client.post(
        f"/api/reunioes/{reuniao['id']}/participantes/{admin['id']}",
        headers=admin["headers"],
    )
    assert adicionado.status_code == 200
    assert len(adicionado.json()["participantes"]) == 2

    removido = client.delete(
        f"/api/reunioes/{reuniao['id']}/participantes/{membro['id']}",
        headers=admin["headers"],
    )
    assert removido.status_code == 200
    assert len(removido.json()["participantes"]) == 1

    atualizada = client.patch(
        f"/api/reunioes/{reuniao['id']}",
        headers=admin["headers"],
        json={"titulo": "Planejamento atualizado"},
    )
    assert atualizada.status_code == 200

    removida = client.delete(
        f"/api/reunioes/{reuniao['id']}", headers=admin["headers"]
    )
    assert removida.status_code == 200


def test_validacao_periodo_reuniao(client, admin):
    resposta = client.post(
        "/api/reunioes/",
        headers=admin["headers"],
        json={
            "titulo": "Reunião inválida",
            "data_hora_inicio": "2030-02-01T11:00:00",
            "data_hora_fim": "2030-02-01T10:00:00",
        },
    )
    assert resposta.status_code == 422
