"""Testes do backlog de itens (bugs, melhorias e tarefas).

Cobre o CRUD de itens do backlog, filtros por status e busca textual, troca de
status, regras de permissão (membro não altera item de outro autor) e validação
de campos obrigatórios/enums.
"""


def test_crud_backlog(client, admin, membro):
    """Valida criação, listagem, filtros, edição e permissões do backlog.

    Cenário: o membro cria um item do tipo BUG, lista por status e por busca,
    altera status e prioridade, o admin altera o mesmo item, o admin cria um
    item próprio que o membro não pode editar, e por fim o admin remove ambos.
    Esperado: status inicial PENDENTE, filtros retornando itens, edições em 200,
    edição indevida em 403 e item removido deixando de existir (404).
    """
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
    # Todo item nasce com status PENDENTE e autor igual ao criador.
    assert item["status"] == "PENDENTE"
    assert item["autor_id"] == membro["id"]

    # Filtro por status PENDENTE.
    listagem = client.get(
        "/api/backlog/?status=PENDENTE", headers=membro["headers"]
    )
    assert listagem.status_code == 200
    assert listagem.json()["total"] >= 1

    # Busca textual pelo título.
    busca = client.get("/api/backlog/?busca=login", headers=membro["headers"])
    assert busca.status_code == 200
    assert busca.json()["total"] >= 1

    # Atualização de status via endpoint dedicado.
    status = client.patch(
        f"/api/backlog/{item['id']}/status",
        headers=membro["headers"],
        json={"status": "EM_ANDAMENTO"},
    )
    assert status.status_code == 200
    assert status.json()["status"] == "EM_ANDAMENTO"

    # O autor pode alterar a prioridade do próprio item.
    atualizado = client.patch(
        f"/api/backlog/{item['id']}",
        headers=membro["headers"],
        json={"prioridade": "MEDIA"},
    )
    assert atualizado.status_code == 200
    assert atualizado.json()["prioridade"] == "MEDIA"

    # O admin também pode editar itens de qualquer autor.
    admin_atualiza = client.patch(
        f"/api/backlog/{item['id']}",
        headers=admin["headers"],
        json={"titulo": "Alterado pelo administrador"},
    )
    assert admin_atualiza.status_code == 200

    # Item criado pelo admin para testar permissão de edição.
    do_admin = client.post(
        "/api/backlog/",
        headers=admin["headers"],
        json={"titulo": "Item do administrador", "tipo": "MELHORIA"},
    )
    assert do_admin.status_code == 201

    # Membro não pode editar item de outro autor.
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

    # Após remover, a consulta direta deve retornar 404.
    inexistente = client.get(
        f"/api/backlog/{item['id']}", headers=admin["headers"]
    )
    assert inexistente.status_code == 404


def test_validacao_backlog(client, membro):
    """Valida as restrições de criação de item do backlog.

    Cenário: envia título curto demais ("ab") e um ``tipo`` inválido.
    Esperado: erro de validação (422).
    """
    resposta = client.post(
        "/api/backlog/",
        headers=membro["headers"],
        json={"titulo": "ab", "tipo": "INVALIDO"},
    )
    assert resposta.status_code == 422
