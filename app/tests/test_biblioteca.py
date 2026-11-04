"""Testes da biblioteca: categorias, pastas e associação de arquivos.

Verifica permissões de administrador para categorias/pastas, unicidade de
categorias, criação de subpastas, bloqueio de exclusão quando há arquivos
vinculados e validação de pasta-pai inexistente.
"""


def test_crud_categorias_e_pastas(client, admin, membro):
    """Valida categorias, pastas/subpastas e dependências com arquivos.

    Cenário: membro tenta criar categoria (proibido), admin cria categoria e
    pasta, tenta duplicar categoria, cria subpasta, lista ambos, edita a pasta,
    faz upload de arquivo vinculado, tenta excluir categoria/pasta (bloqueado)
    e, após remover arquivo e subpasta, consegue excluir pasta e categoria.
    Esperado: 403 para membro, 409 em duplicidades e exclusões bloqueadas, 201
    nas criações, 200 nas listagens/edições e exclusões finais com sucesso.
    """
    # Membro comum não tem permissão para criar categorias.
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

    # O nome de categoria é único: duplicar deve gerar conflito (409).
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

    # Subpasta referencia a pasta criada via pasta_pai_id.
    subpasta = client.post(
        "/api/pastas/",
        headers=admin["headers"],
        json={"nome": "2026", "pasta_pai_id": pasta_id},
    )
    assert subpasta.status_code == 201, subpasta.text

    # Membro pode visualizar categorias e pastas, mesmo sem criar.
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

    # Upload de arquivo vinculado à categoria e à pasta (IDs enviados como texto
    # porque o corpo é multipart/form-data).
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

    # Categoria/pasta com arquivos vinculados não podem ser excluídas (409).
    categoria_bloqueada = client.delete(
        f"/api/categorias/{categoria_id}", headers=admin["headers"]
    )
    assert categoria_bloqueada.status_code == 409

    pasta_bloqueada = client.delete(
        f"/api/pastas/{pasta_id}", headers=admin["headers"]
    )
    assert pasta_bloqueada.status_code == 409

    # Remove as dependências (arquivo e subpasta) antes de excluir a pasta.
    client.delete(f"/api/arquivos/{arquivo_id}", headers=admin["headers"])
    client.delete(f"/api/pastas/{subpasta.json()['id']}", headers=admin["headers"])

    # Sem dependências, a pasta e a categoria podem ser removidas.
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
    """Garante validação ao referenciar uma pasta-pai inexistente.

    Cenário: cria uma pasta apontando para ``pasta_pai_id`` que não existe.
    Esperado: 404 (recurso pai não encontrado).
    """
    resposta = client.post(
        "/api/pastas/",
        headers=admin["headers"],
        json={"nome": "Órfã", "pasta_pai_id": 99999},
    )
    assert resposta.status_code == 404
