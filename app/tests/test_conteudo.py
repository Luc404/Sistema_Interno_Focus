def test_crud_notebook(client, admin, membro):
    criado = client.post(
        "/api/notebooks/",
        headers=membro["headers"],
        json={
            "grupo": "PROJETOS",
            "titulo": "Anotações do projeto Orion",
            "subtitulo": "Reunião inicial",
            "conteudo": "Definir escopo e cronograma do projeto.",
            "tags": "orion,planejamento",
        },
    )
    assert criado.status_code == 201, criado.text
    notebook = criado.json()

    listagem = client.get(
        "/api/notebooks/?busca=Orion", headers=admin["headers"]
    )
    assert listagem.status_code == 200
    assert listagem.json()["total"] >= 1

    atualizado = client.patch(
        f"/api/notebooks/{notebook['id']}",
        headers=membro["headers"],
        json={"conteudo": "Escopo revisado e aprovado."},
    )
    assert atualizado.status_code == 200
    assert "revisado" in atualizado.json()["conteudo"]

    admin_atualiza = client.patch(
        f"/api/notebooks/{notebook['id']}",
        headers=admin["headers"],
        json={"titulo": "Alterado por admin"},
    )
    assert admin_atualiza.status_code == 200

    do_admin = client.post(
        "/api/notebooks/",
        headers=admin["headers"],
        json={"titulo": "Notebook do admin", "conteudo": "Conteúdo privado"},
    )
    assert do_admin.status_code == 201

    proibido = client.patch(
        f"/api/notebooks/{do_admin.json()['id']}",
        headers=membro["headers"],
        json={"titulo": "Tentativa indevida"},
    )
    assert proibido.status_code == 403

    client.delete(
        f"/api/notebooks/{do_admin.json()['id']}", headers=admin["headers"]
    )

    removido = client.delete(
        f"/api/notebooks/{notebook['id']}", headers=admin["headers"]
    )
    assert removido.status_code == 200


def test_crud_chatbot(client, admin, membro):
    criado = client.post(
        "/api/chatbots/",
        headers=admin["headers"],
        json={
            "nome": "Assistente Focus",
            "descricao": "Ajuda interna",
            "versao": "v1.0",
            "status": "ACTIVE",
            "modelo": "gpt-4o",
        },
    )
    assert criado.status_code == 201, criado.text
    chatbot = criado.json()

    listagem = client.get(
        "/api/chatbots/?status=ACTIVE", headers=membro["headers"]
    )
    assert listagem.status_code == 200
    assert listagem.json()["total"] >= 1

    resposta = client.post(
        f"/api/chatbots/{chatbot['id']}/mensagens",
        headers=membro["headers"],
        json={"conteudo": "Como faço para cadastrar um cliente?"},
    )
    assert resposta.status_code == 200, resposta.text
    dados = resposta.json()
    assert dados["mensagem_usuario"]["papel"] == "USER"
    assert dados["resposta"]["papel"] == "ASSISTANT"

    mensagens = client.get(
        f"/api/chatbots/{chatbot['id']}/mensagens", headers=membro["headers"]
    )
    assert mensagens.status_code == 200
    assert mensagens.json()["total"] >= 2

    proibido = client.post(
        "/api/chatbots/",
        headers=membro["headers"],
        json={"nome": "Bot do membro"},
    )
    assert proibido.status_code == 403

    removido = client.delete(
        f"/api/chatbots/{chatbot['id']}", headers=admin["headers"]
    )
    assert removido.status_code == 200


def test_notificacoes(client, admin, membro):
    criada = client.post(
        "/api/notificacoes/",
        headers=admin["headers"],
        json={
            "usuario_id": membro["id"],
            "titulo": "Nova tarefa atribuída",
            "mensagem": "Você recebeu uma nova tarefa.",
            "tipo": "TAREFA",
            "link": "/tarefas/1",
        },
    )
    assert criada.status_code == 201, criada.text
    notificacao = criada.json()

    minhas = client.get(
        "/api/notificacoes/minhas?lida=false", headers=membro["headers"]
    )
    assert minhas.status_code == 200
    assert any(item["id"] == notificacao["id"] for item in minhas.json()["items"])

    lida = client.patch(
        f"/api/notificacoes/{notificacao['id']}/ler", headers=membro["headers"]
    )
    assert lida.status_code == 200
    assert lida.json()["lida"] is True

    todas = client.patch("/api/notificacoes/ler-todas", headers=membro["headers"])
    assert todas.status_code == 200

    removida = client.delete(
        f"/api/notificacoes/{notificacao['id']}", headers=membro["headers"]
    )
    assert removida.status_code == 200

    proibida = client.post(
        "/api/notificacoes/",
        headers=membro["headers"],
        json={
            "usuario_id": membro["id"],
            "titulo": "Sem permissão",
            "mensagem": "Não deveria criar",
        },
    )
    assert proibida.status_code == 403


def test_dashboard_e_busca(client, admin):
    dashboard = client.get("/api/dashboard/resumo", headers=admin["headers"])
    assert dashboard.status_code == 200
    dados = dashboard.json()
    for campo in (
        "usuarios_ativos",
        "setores_ativos",
        "arquivos",
        "itens_backlog",
        "mensalidades_pendentes",
        "tarefas_pendentes",
        "reunioes_hoje",
        "chatbots_ativos",
        "notebooks",
        "notificacoes_nao_lidas",
        "proximas_reunioes",
    ):
        assert campo in dados

    criado = client.post(
        "/api/notebooks/",
        headers=admin["headers"],
        json={
            "titulo": "Manual de integração Zebra",
            "conteudo": "Passos para integração com o sistema Zebra.",
        },
    )
    assert criado.status_code == 201

    busca = client.get("/api/busca/?q=Zebra", headers=admin["headers"])
    assert busca.status_code == 200
    assert busca.json()["total"] >= 1
    assert any(item["tipo"] == "notebook" for item in busca.json()["resultados"])

    client.delete(f"/api/notebooks/{criado.json()['id']}", headers=admin["headers"])
