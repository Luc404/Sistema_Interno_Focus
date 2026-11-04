"""Testes de agenda: tarefas pessoais, links e reuniões.

Cobre o CRUD de tarefas pessoais (com troca de status), o CRUD de links com
filtro por categoria e o ciclo completo de reuniões, incluindo gestão de
participantes e validação do período (início antes do fim).
"""


def test_crud_tarefa_pessoal(client, admin, membro):
    """Valida o CRUD de uma tarefa pessoal pertencente ao membro.

    Cenário: o membro cria uma tarefa, lista as suas, o admin consulta as
    tarefas do membro, o membro marca como concluída e por fim a remove.
    Esperado: criação em 201 com o dono correto, listagens em 200, status
    atualizado para CONCLUIDA e exclusão em 200.
    """
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
    # A tarefa criada deve pertencer ao membro autenticado.
    assert tarefa["usuario_id"] == membro["id"]

    # Lista "minhas tarefas" do próprio membro.
    minhas = client.get(
        "/api/tarefas-pessoais/minhas", headers=membro["headers"]
    )
    assert minhas.status_code == 200
    assert minhas.json()["total"] >= 1

    # Admin consulta as tarefas de um usuário específico.
    do_usuario = client.get(
        f"/api/tarefas-pessoais/usuario/{membro['id']}",
        headers=admin["headers"],
    )
    assert do_usuario.status_code == 200

    # Atualização de status via endpoint dedicado.
    status = client.patch(
        f"/api/tarefas-pessoais/{tarefa['id']}/status",
        headers=membro["headers"],
        json={"status": "CONCLUIDA"},
    )
    assert status.status_code == 200
    assert status.json()["status"] == "CONCLUIDA"

    # Remoção da tarefa pelo próprio dono.
    removida = client.delete(
        f"/api/tarefas-pessoais/{tarefa['id']}", headers=membro["headers"]
    )
    assert removida.status_code == 200


def test_crud_link(client, membro):
    """Valida o CRUD de um link salvo pelo membro.

    Cenário: cria um link, filtra a listagem por categoria, atualiza a
    descrição e o remove. Esperado: 201 na criação, listagem com pelo menos um
    item, descrição alterada e exclusão em 200.
    """
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

    # A listagem deve respeitar o filtro por categoria.
    listagem = client.get("/api/links/?categoria=Backend", headers=membro["headers"])
    assert listagem.status_code == 200
    assert listagem.json()["total"] >= 1

    # Atualização parcial: somente a descrição é modificada.
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
    """Valida o ciclo completo de uma reunião com participantes.

    Cenário: o admin cria uma reunião com o membro como participante, lista e
    consulta as próximas, adiciona o admin, remove o membro, atualiza o título
    e exclui a reunião. Esperado: participantes gerenciados corretamente e
    todas as operações retornando sucesso.
    """
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
    # A reunião deve ter sido criada com exatamente um participante (o membro).
    assert len(reuniao["participantes"]) == 1
    assert reuniao["participantes"][0]["id"] == membro["id"]

    # Busca textual pelo título, acessível ao membro.
    listagem = client.get("/api/reunioes/?busca=Planejamento", headers=membro["headers"])
    assert listagem.status_code == 200
    assert listagem.json()["total"] >= 1

    # O membro deve enxergar a reunião na lista de próximas.
    proximas = client.get("/api/reunioes/proximas", headers=membro["headers"])
    assert proximas.status_code == 200
    assert any(item["id"] == reuniao["id"] for item in proximas.json())

    # Consulta explícita dos participantes da reunião.
    participantes = client.get(
        f"/api/reunioes/{reuniao['id']}/participantes",
        headers=membro["headers"],
    )
    assert participantes.status_code == 200
    assert len(participantes.json()) == 1

    # Adiciona o admin como participante; agora devem existir dois.
    adicionado = client.post(
        f"/api/reunioes/{reuniao['id']}/participantes/{admin['id']}",
        headers=admin["headers"],
    )
    assert adicionado.status_code == 200
    assert len(adicionado.json()["participantes"]) == 2

    # Remove o membro; volta a existir apenas o admin.
    removido = client.delete(
        f"/api/reunioes/{reuniao['id']}/participantes/{membro['id']}",
        headers=admin["headers"],
    )
    assert removido.status_code == 200
    assert len(removido.json()["participantes"]) == 1

    # Atualização parcial do título.
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
    """Garante que o período da reunião é validado.

    Cenário: tentativa de criar reunião com o horário de fim anterior ao de
    início. Esperado: erro de validação (422).
    """
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
