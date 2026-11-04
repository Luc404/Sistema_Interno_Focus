"""Testes de conteúdo: notebooks, chatbots, notificações, dashboard e busca.

Cobre o CRUD de notebooks e suas permissões, o gerenciamento de chatbots e o
envio/consulta de mensagens, o fluxo de notificações (criar, listar, marcar como
lida, ler todas e remover), o resumo do dashboard e a busca global.
"""


def test_crud_notebook(client, admin, membro):
    """Valida o CRUD de notebooks e as regras de autoria.

    Cenário: o membro cria um notebook, o admin lista por busca, o membro edita
    o conteúdo, o admin também edita, o admin cria um notebook próprio que o
    membro não pode alterar, e por fim o admin remove ambos.
    Esperado: 201 na criação, listagem com resultados, edições em 200, edição
    indevida em 403 e remoção em 200.
    """
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

    # A busca textual deve encontrar o notebook pelo título.
    listagem = client.get(
        "/api/notebooks/?busca=Orion", headers=admin["headers"]
    )
    assert listagem.status_code == 200
    assert listagem.json()["total"] >= 1

    # O autor edita o conteúdo do próprio notebook.
    atualizado = client.patch(
        f"/api/notebooks/{notebook['id']}",
        headers=membro["headers"],
        json={"conteudo": "Escopo revisado e aprovado."},
    )
    assert atualizado.status_code == 200
    assert "revisado" in atualizado.json()["conteudo"]

    # O admin também pode editar notebooks de terceiros.
    admin_atualiza = client.patch(
        f"/api/notebooks/{notebook['id']}",
        headers=admin["headers"],
        json={"titulo": "Alterado por admin"},
    )
    assert admin_atualiza.status_code == 200

    # Notebook criado pelo admin para testar permissão de edição.
    do_admin = client.post(
        "/api/notebooks/",
        headers=admin["headers"],
        json={"titulo": "Notebook do admin", "conteudo": "Conteúdo privado"},
    )
    assert do_admin.status_code == 201

    # Membro não pode editar notebook de outro autor.
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
    """Valida criação de chatbot, envio de mensagens e permissões.

    Cenário: o admin cria um chatbot ativo, o membro lista por status, envia
    uma mensagem (o backend gera resposta do assistente), consulta o histórico,
    tenta criar chatbot (proibido) e o admin remove o chatbot.
    Esperado: criação restrita ao admin, mensagens com papéis USER/ASSISTANT,
    histórico com pelo menos duas mensagens e exclusão em 200.
    """
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

    # Filtro por status do chatbot.
    listagem = client.get(
        "/api/chatbots/?status=ACTIVE", headers=membro["headers"]
    )
    assert listagem.status_code == 200
    assert listagem.json()["total"] >= 1

    # Envio de mensagem: deve registrar a mensagem do usuário e gerar resposta.
    resposta = client.post(
        f"/api/chatbots/{chatbot['id']}/mensagens",
        headers=membro["headers"],
        json={"conteudo": "Como faço para cadastrar um cliente?"},
    )
    assert resposta.status_code == 200, resposta.text
    dados = resposta.json()
    assert dados["mensagem_usuario"]["papel"] == "USER"
    assert dados["resposta"]["papel"] == "ASSISTANT"

    # Histórico deve conter ao menos a mensagem do usuário e a resposta.
    mensagens = client.get(
        f"/api/chatbots/{chatbot['id']}/mensagens", headers=membro["headers"]
    )
    assert mensagens.status_code == 200
    assert mensagens.json()["total"] >= 2

    # Somente administradores podem criar chatbots.
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
    """Valida o fluxo de notificações de um usuário.

    Cenário: o admin cria uma notificação para o membro, o membro lista as não
    lidas, marca uma como lida, marca todas como lidas, remove a notificação e
    tenta criar outra (proibido). Esperado: criação restrita ao admin (403 para
    membro), notificação presente na listagem, ``lida`` virando True e remoção
    em 200.
    """
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

    # O membro deve ver a notificação entre as suas não lidas.
    minhas = client.get(
        "/api/notificacoes/minhas?lida=false", headers=membro["headers"]
    )
    assert minhas.status_code == 200
    assert any(item["id"] == notificacao["id"] for item in minhas.json()["items"])

    # Marca uma notificação específica como lida.
    lida = client.patch(
        f"/api/notificacoes/{notificacao['id']}/ler", headers=membro["headers"]
    )
    assert lida.status_code == 200
    assert lida.json()["lida"] is True

    # Marca todas as notificações do usuário como lidas.
    todas = client.patch("/api/notificacoes/ler-todas", headers=membro["headers"])
    assert todas.status_code == 200

    removida = client.delete(
        f"/api/notificacoes/{notificacao['id']}", headers=membro["headers"]
    )
    assert removida.status_code == 200

    # Membro não tem permissão para criar notificações para outros usuários.
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
    """Valida o resumo do dashboard e a busca global.

    Cenário: consulta o resumo do dashboard, cria um notebook com termo único e
    pesquisa por esse termo. Esperado: todos os campos esperados presentes no
    resumo, busca com resultados incluindo um item do tipo "notebook", e o
    notebook é removido ao final para não afetar outros testes.
    """
    dashboard = client.get("/api/dashboard/resumo", headers=admin["headers"])
    assert dashboard.status_code == 200
    dados = dashboard.json()
    # O resumo precisa expor todas as métricas esperadas pelo frontend.
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

    # A busca global deve encontrar o notebook recém-criado pelo termo único.
    busca = client.get("/api/busca/?q=Zebra", headers=admin["headers"])
    assert busca.status_code == 200
    assert busca.json()["total"] >= 1
    assert any(item["tipo"] == "notebook" for item in busca.json()["resultados"])

    client.delete(f"/api/notebooks/{criado.json()['id']}", headers=admin["headers"])
