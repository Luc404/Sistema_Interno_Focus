def test_membro_nao_pode_criar_mensalidade(client, membro):
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
    assert mensalidade["status_pagamento"] == "PENDENTE"

    listagem = client.get(
        "/api/mensalidades/?status_pagamento=PENDENTE",
        headers=membro["headers"],
    )
    assert listagem.status_code == 200
    assert listagem.json()["total"] >= 1

    resumo = client.get("/api/mensalidades/resumo", headers=membro["headers"])
    assert resumo.status_code == 200
    assert resumo.json()["total"] >= 1

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
