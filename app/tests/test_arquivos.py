def test_upload_download_e_exclusao_de_arquivo(client, membro):
    criado = client.post(
        "/api/arquivos/upload",
        headers=membro["headers"],
        files={"arquivo": ("documento.txt", b"conteudo de teste", "text/plain")},
        data={"titulo": "Documento de teste", "categoria": "Testes"},
    )
    assert criado.status_code == 201, criado.text
    arquivo = criado.json()
    assert arquivo["titulo"] == "Documento de teste"
    assert arquivo["tamanho_bytes"] == len(b"conteudo de teste")
    assert arquivo["usuario_id"] == membro["id"]

    listagem = client.get(
        "/api/arquivos/?categoria=Testes", headers=membro["headers"]
    )
    assert listagem.status_code == 200
    assert listagem.json()["total"] >= 1

    download = client.get(
        f"/api/arquivos/{arquivo['id']}/download", headers=membro["headers"]
    )
    assert download.status_code == 200
    assert download.content == b"conteudo de teste"

    atualizado = client.patch(
        f"/api/arquivos/{arquivo['id']}",
        headers=membro["headers"],
        json={"titulo": "Documento renomeado"},
    )
    assert atualizado.status_code == 200
    assert atualizado.json()["titulo"] == "Documento renomeado"

    removido = client.delete(
        f"/api/arquivos/{arquivo['id']}", headers=membro["headers"]
    )
    assert removido.status_code == 200

    inexistente = client.get(
        f"/api/arquivos/{arquivo['id']}", headers=membro["headers"]
    )
    assert inexistente.status_code == 404


def test_upload_sem_titulo(client, membro):
    resposta = client.post(
        "/api/arquivos/upload",
        headers=membro["headers"],
        files={"arquivo": ("vazio.txt", b"x", "text/plain")},
    )
    assert resposta.status_code == 422
