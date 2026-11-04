"""Testes do módulo financeiro (mensalidades de clientes).

Verifica a restrição de criação a administradores, o CRUD/busca/resumo de
mensalidades, o registro de pagamento e a validação de valores inválidos.
"""


def test_membro_nao_pode_criar_mensalidade(client, membro):
    """Garante que membros não podem cadastrar mensalidades.

    Cenário: o membro tenta criar uma mensalidade. Esperado: 403.
    """
    resposta = client.post(
        "/api/mensalidades/",
        headers=membro["headers"],
        json={
            "nome_cliente": "Cliente Teste",
            "valor": 100,
            "data_vencimento": "2030-03-10T00:00:00",
        },
    )
    assert resposta.status_code == 403


def test_crud_mensalidade(client, admin, membro):
    """Valida o ciclo de uma mensalidade, incluindo o pagamento.

    Cenário: o admin cria uma mensalidade, o membro lista por status e consulta
    o resumo, o admin registra o pagamento e por fim exclui a mensalidade.
    Esperado: criação em 201 com status PENDENTE e valor preservado, listagem/
    resumo em 200, pagamento mudando o status para PAGO com data preenchida e
    exclusão em 200.
    """
    criada = client.post(
        "/api/mensalidades/",
        headers=admin["headers"],
        json={
            "nome_cliente": "Cliente Teste",
            "valor": 150.50,
            "data_vencimento": "2030-03-10T00:00:00",
            "observacao": "Mensalidade de março",
        },
    )
    assert criada.status_code == 201, criada.text
    mensalidade = criada.json()
    assert mensalidade["valor"] == 150.5
    # Toda mensalidade é criada como pendente até o registro do pagamento.
    assert mensalidade["status_pagamento"] == "PENDENTE"

    # Membro pode consultar a listagem filtrada por status.
    listagem = client.get(
        "/api/mensalidades/?status_pagamento=PENDENTE",
        headers=membro["headers"],
    )
    assert listagem.status_code == 200
    assert listagem.json()["total"] >= 1

    # Resumo financeiro acessível ao membro.
    resumo = client.get("/api/mensalidades/resumo", headers=membro["headers"])
    assert resumo.status_code == 200
    assert resumo.json()["total"] >= 1

    # Registro do pagamento: status muda para PAGO e a data é preenchida.
    paga = client.patch(
        f"/api/mensalidades/{mensalidade['id']}/pagar",
        headers=admin["headers"],
        json={"data_pagamento": "2030-03-05T12:00:00"},
    )
    assert paga.status_code == 200
    assert paga.json()["status_pagamento"] == "PAGO"
    assert paga.json()["data_pagamento"] is not None

    removida = client.delete(
        f"/api/mensalidades/{mensalidade['id']}", headers=admin["headers"]
    )
    assert removida.status_code == 200


def test_valor_invalido_mensalidade(client, admin):
    """Valida a rejeição de mensalidade com valor zero.

    Cenário: o admin tenta criar uma mensalidade com ``valor`` igual a 0.
    Esperado: erro de validação (422).
    """
    resposta = client.post(
        "/api/mensalidades/",
        headers=admin["headers"],
        json={
            "nome_cliente": "Cliente Teste",
            "valor": 0,
            "data_vencimento": "2030-03-10T00:00:00",
        },
    )
    assert resposta.status_code == 422
