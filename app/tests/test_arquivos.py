"""Testes de arquivos: upload, download, listagem, edição e exclusão.

Verifica o fluxo completo de armazenamento de arquivos, incluindo a gravação
física no diretório temporário configurado, o download do conteúdo e a
validação de campos obrigatórios no upload.
"""


def test_upload_download_e_exclusao_de_arquivo(client, membro):
    """Percorre o ciclo de vida completo de um arquivo enviado pelo membro.

    Cenário: faz upload de um arquivo de texto, lista por categoria, baixa o
    conteúdo, renomeia o título, exclui o registro e tenta consultá-lo de novo.
    Esperado: upload em 201 com metadados corretos, download idêntico ao enviado,
    edição aplicada, exclusão em 200 e consulta posterior retornando 404.
    """
    criado = client.post(
        "/api/arquivos/upload",
        headers=membro["headers"],
        # files envia o conteúdo binário; data envia os campos do formulário.
        files={"arquivo": ("documento.txt", b"conteudo de teste", "text/plain")},
        data={"titulo": "Documento de teste", "categoria": "Testes"},
    )
    assert criado.status_code == 201, criado.text
    arquivo = criado.json()
    # Metadados devem refletir exatamente o que foi enviado.
    assert arquivo["titulo"] == "Documento de teste"
    assert arquivo["tamanho_bytes"] == len(b"conteudo de teste")
    assert arquivo["usuario_id"] == membro["id"]

    # Listagem filtrada pela categoria informada no upload.
    listagem = client.get(
        "/api/arquivos/?categoria=Testes", headers=membro["headers"]
    )
    assert listagem.status_code == 200
    assert listagem.json()["total"] >= 1

    # O download deve devolver exatamente os bytes originais.
    download = client.get(
        f"/api/arquivos/{arquivo['id']}/download", headers=membro["headers"]
    )
    assert download.status_code == 200
    assert download.content == b"conteudo de teste"

    # Atualização parcial apenas do título.
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

    # Após a exclusão, o arquivo não deve mais existir.
    inexistente = client.get(
        f"/api/arquivos/{arquivo['id']}", headers=membro["headers"]
    )
    assert inexistente.status_code == 404


def test_upload_sem_titulo(client, membro):
    """Valida que o título é obrigatório no upload de arquivos.

    Cenário: envia um arquivo sem o campo ``titulo``. Esperado: erro de
    validação (422).
    """
    resposta = client.post(
        "/api/arquivos/upload",
        headers=membro["headers"],
        files={"arquivo": ("vazio.txt", b"x", "text/plain")},
    )
    assert resposta.status_code == 422
