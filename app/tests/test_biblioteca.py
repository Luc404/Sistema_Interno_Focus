def test_crud_categorias_e_pastas(client, admin, membro):
    proibida = client.post(
        "/api/categorias/",
        headers=membro["headers"],
        json={"nome": "Sem permissão"},
    )
    assert proibida.status_code == 403

    categoria = client.post(
        "/api/categorias/",
        headers=admin["headers"],
        json={"nome": "Contratos", "descricao": "Documentos contratuais"},
    )
    assert categoria.status_code == 201, categoria.text
    categoria_id = categoria.json()["id"]

    duplicada = client.post(
        "/api/categorias/",
        headers=admin["headers"],
        json={"nome": "Contratos"},
    )
    assert duplicada.status_code == 409

    pasta = client.post(
        "/api/pastas/",
        headers=admin["headers"],
        json={"nome": "Clientes", "descricao": "Documentos por cliente"},
    )
    assert pasta.status_code == 201, pasta.text
    pasta_id = pasta.json()["id"]

    subpasta = client.post(
        "/api/pastas/",
        headers=admin["headers"],
        json={"nome": "2026", "pasta_pai_id": pasta_id},
    )
    assert subpasta.status_code == 201, subpasta.text

    listagem = client.get("/api/categorias/?busca=Contratos", headers=membro["headers"])
    assert listagem.status_code == 200
    assert listagem.json()["total"] >= 1

    pastas = client.get("/api/pastas/?busca=Clientes", headers=membro["headers"])
    assert pastas.status_code == 200
    assert pastas.json()["total"] >= 1

    atualizada = client.patch(
        f"/api/pastas/{pasta_id}",
        headers=admin["headers"],
        json={"descricao": "Documentos organizados por cliente"},
    )
    assert atualizada.status_code == 200

    arquivo = client.post(
        "/api/arquivos/upload",
        headers=admin["headers"],
        files={"arquivo": ("contrato.txt", b"contrato", "text/plain")},
        data={
            "titulo": "Contrato modelo",
            "categoria_id": str(categoria_id),
            "pasta_id": str(pasta_id),
        },
    )
    assert arquivo.status_code == 201, arquivo.text
    arquivo_id = arquivo.json()["id"]

    categoria_bloqueada = client.delete(
        f"/api/categorias/{categoria_id}", headers=admin["headers"]
    )
    assert categoria_bloqueada.status_code == 409

    pasta_bloqueada = client.delete(
        f"/api/pastas/{pasta_id}", headers=admin["headers"]
    )
    assert pasta_bloqueada.status_code == 409

    client.delete(f"/api/arquivos/{arquivo_id}", headers=admin["headers"])
    client.delete(f"/api/pastas/{subpasta.json()['id']}", headers=admin["headers"])

    assert (
        client.delete(f"/api/pastas/{pasta_id}", headers=admin["headers"]).status_code
        == 200
    )
    assert (
        client.delete(
            f"/api/categorias/{categoria_id}", headers=admin["headers"]
        ).status_code
        == 200
    )


def test_pasta_pai_inexistente(client, admin):
    resposta = client.post(
        "/api/pastas/",
        headers=admin["headers"],
        json={"nome": "Órfã", "pasta_pai_id": 99999},
    )
    assert resposta.status_code == 404
