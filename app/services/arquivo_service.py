"""Serviço de arquivos da biblioteca.

Centraliza o cadastro, a listagem paginada, o upload físico, a atualização,
o download e a exclusão de arquivos, validando vínculos com categorias e
pastas e aplicando os limites de tamanho configurados.
"""

import mimetypes
from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.validators import validar_setor  # noqa: F401  (mantém utilitário disponível)
from app.model.biblioteca import Arquivo
from app.model.categoria import Categoria, Pasta
from app.schemas.arquivo_schema import ArquivoCreate
from app.services.common_service import montar_pagina, paginar


def obter_arquivo(db: Session, arquivo_id: int) -> Arquivo | None:
    """Busca um arquivo pelo identificador, retornando None se não existir.

    Args:
        db: Sessão do SQLAlchemy usada para acesso ao banco.
        arquivo_id: Identificador primário do arquivo.

    Returns:
        A instância de ``Arquivo`` encontrada ou ``None`` quando o ID não existe.

    Raises:
        Nenhuma exceção é levantada explicitamente; eventuais erros de conexão
        com o banco são propagados pelo SQLAlchemy.
    """
    # db.get faz busca direta pela chave primária, sem montar uma query completa.
    return db.get(Arquivo, arquivo_id)


def listar_arquivos(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    busca: str | None = None,
    categoria: str | None = None,
    categoria_id: int | None = None,
    pasta_id: int | None = None,
    usuario_id: int | None = None,
):
    """Lista arquivos com paginação e filtros opcionais.

    Os filtros são combinados de forma aditiva (AND): cada parâmetro informado
    restringe ainda mais o conjunto de resultados.

    Args:
        db: Sessão do SQLAlchemy.
        skip: Quantidade de registros a ignorar (offset da paginação).
        limit: Quantidade máxima de registros a retornar.
        busca: Texto parcial para pesquisar no título (case-insensitive).
        categoria: Nome exato da categoria textual do arquivo.
        categoria_id: ID da categoria relacionada.
        pasta_id: ID da pasta relacionada.
        usuario_id: ID do usuário dono do arquivo.

    Returns:
        Um objeto ``Page`` contendo os itens da página e o total de registros
        que atendem aos filtros.

    Raises:
        Nenhuma exceção de negócio; erros de banco são propagados.
    """
    # Base da consulta: todos os arquivos, sem filtros aplicados ainda.
    query = db.query(Arquivo)
    if busca:
        # ilike -> comparação case-insensitive usando curingas SQL (%texto%).
        query = query.filter(Arquivo.titulo.ilike(f"%{busca}%"))
    if categoria:
        # Filtro por nome textual da categoria (coluna legada/denormalizada).
        query = query.filter(Arquivo.categoria == categoria)
    if categoria_id is not None:
        # Filtro pelo vínculo relacional com Categoria.
        query = query.filter(Arquivo.categoria_id == categoria_id)
    if pasta_id is not None:
        # Filtro pelo vínculo relacional com Pasta.
        query = query.filter(Arquivo.pasta_id == pasta_id)
    if usuario_id is not None:
        # Filtro pelo dono do arquivo (usado para escopo por usuário).
        query = query.filter(Arquivo.usuario_id == usuario_id)

    # Ordena do upload mais recente para o mais antigo.
    query = query.order_by(Arquivo.data_upload.desc())
    # paginar executa o count total e aplica offset/limit na query.
    items, total = paginar(query, skip, limit)
    return montar_pagina(items, total, skip, limit)


def _validar_categoria_pasta(db: Session, categoria_id: int | None, pasta_id: int | None) -> None:
    """Valida que a categoria e a pasta informadas existem no banco.

    Args:
        db: Sessão do SQLAlchemy.
        categoria_id: ID da categoria a validar (pode ser ``None``).
        pasta_id: ID da pasta a validar (pode ser ``None``).

    Returns:
        ``None`` quando os vínculos são válidos ou não foram informados.

    Raises:
        HTTPException: 404 quando a categoria ou a pasta não existem.
    """
    # Só consulta o banco quando um vínculo foi efetivamente informado.
    if categoria_id is not None and not db.get(Categoria, categoria_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Categoria não encontrada")
    if pasta_id is not None and not db.get(Pasta, pasta_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pasta não encontrada")


def criar_arquivo(db: Session, arquivo_dto: ArquivoCreate, usuario_id: int) -> Arquivo:
    """Cadastra metadados de um arquivo já existente (sem upload físico).

    Args:
        db: Sessão do SQLAlchemy.
        arquivo_dto: Dados de criação do arquivo.
        usuario_id: ID do usuário que está cadastrando o arquivo.

    Returns:
        A instância de ``Arquivo`` persistida e recarregada do banco.

    Raises:
        HTTPException: 404 quando categoria/pasta informadas não existem.
        Erros de integridade/banco são propagados pelo SQLAlchemy.
    """
    # Garante que os vínculos opcionais apontem para registros existentes.
    _validar_categoria_pasta(db, arquivo_dto.categoria_id, arquivo_dto.pasta_id)
    novo_arquivo = Arquivo(
        titulo=arquivo_dto.titulo,
        categoria=arquivo_dto.categoria,
        categoria_id=arquivo_dto.categoria_id,
        pasta_id=arquivo_dto.pasta_id,
        caminho_arquivo=arquivo_dto.caminho_arquivo,
        tipo_mime=arquivo_dto.tipo_mime,
        tamanho_bytes=arquivo_dto.tamanho_bytes,
        usuario_id=usuario_id,
    )
    db.add(novo_arquivo)
    # commit efetiva a transação; refresh recarrega campos gerados pelo banco
    # (como o ID e timestamps default).
    db.commit()
    db.refresh(novo_arquivo)
    return novo_arquivo


def salvar_upload(
    db: Session,
    upload: UploadFile,
    titulo: str,
    usuario_id: int,
    categoria: str | None = None,
    categoria_id: int | None = None,
    pasta_id: int | None = None,
) -> Arquivo:
    """Grava fisicamente o conteúdo de um upload e cadastra seus metadados.

    O arquivo é salvo em disco com um nome aleatório (UUID) para evitar
    colisões e preservar apenas a extensão original. O tamanho é controlado
    durante a leitura em blocos, abortando se ultrapassar o limite configurado.

    Args:
        db: Sessão do SQLAlchemy.
        upload: Arquivo recebido via multipart/form-data.
        titulo: Título exibido na biblioteca.
        usuario_id: ID do usuário dono do arquivo.
        categoria: Nome textual da categoria (opcional).
        categoria_id: ID da categoria relacionada (opcional).
        pasta_id: ID da pasta relacionada (opcional).

    Returns:
        A instância de ``Arquivo`` persistida com caminho e tamanho reais.

    Raises:
        HTTPException: 404 para categoria/pasta inexistente, 400 quando o upload
            não possui nome e 413 quando o arquivo excede o limite de tamanho.
        Qualquer outra exceção durante a escrita é propagada após remover o
        arquivo parcialmente gravado.
    """
    settings = get_settings()
    # Valida vínculos antes de gravar qualquer byte em disco.
    _validar_categoria_pasta(db, categoria_id, pasta_id)

    if not upload.filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Arquivo sem nome")

    # Extrai apenas a extensão original (em minúsculas) para compor o nome seguro.
    extensao = Path(upload.filename).suffix.lower()
    # UUID4 evita sobrescrita e nomes previsíveis no diretório de upload.
    nome_seguro = f"{uuid4().hex}{extensao}"
    destino = settings.upload_path / nome_seguro

    tamanho = 0
    try:
        # Abre o destino em modo binário de escrita.
        with destino.open("wb") as saida:
            # Lê em blocos de 1 MiB para não carregar arquivos grandes na memória.
            while chunk := upload.file.read(1024 * 1024):
                tamanho += len(chunk)
                # Interrompe assim que o limite configurado for excedido.
                if tamanho > settings.max_upload_size_bytes:
                    raise HTTPException(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        detail=f"O arquivo excede o limite de {settings.max_upload_size_mb} MB",
                    )
                saida.write(chunk)
    except Exception:
        # Em caso de falha, remove o arquivo parcial e propaga o erro original.
        destino.unlink(missing_ok=True)
        raise

    # Determina o MIME: prioriza o informado no upload, tenta inferir pela
    # extensão e, por fim, usa o tipo binário genérico.
    tipo_mime = (
        upload.content_type
        or mimetypes.guess_type(upload.filename)[0]
        or "application/octet-stream"
    )

    arquivo = Arquivo(
        titulo=titulo,
        categoria=categoria,
        categoria_id=categoria_id,
        pasta_id=pasta_id,
        caminho_arquivo=str(destino),
        tipo_mime=tipo_mime,
        tamanho_bytes=tamanho,
        usuario_id=usuario_id,
    )
    db.add(arquivo)
    db.commit()
    db.refresh(arquivo)
    return arquivo


def atualizar_arquivo(db: Session, arquivo: Arquivo, dados: dict) -> Arquivo:
    """Atualiza parcialmente os campos de um arquivo.

    Args:
        db: Sessão do SQLAlchemy.
        arquivo: Instância já carregada que será modificada.
        dados: Dicionário com os campos a alterar (apenas chaves presentes).

    Returns:
        A instância de ``Arquivo`` atualizada e recarregada do banco.

    Raises:
        HTTPException: 404 quando categoria/pasta informadas não existem.
    """
    # Se algum vínculo está sendo alterado, valida os valores efetivos
    # (usando o valor atual do registro quando a chave não veio no payload).
    if "categoria_id" in dados or "pasta_id" in dados:
        _validar_categoria_pasta(
            db,
            dados.get("categoria_id", arquivo.categoria_id),
            dados.get("pasta_id", arquivo.pasta_id),
        )
    # Aplica dinamicamente cada campo recebido no objeto ORM.
    for campo, valor in dados.items():
        setattr(arquivo, campo, valor)
    db.commit()
    db.refresh(arquivo)
    return arquivo


def caminho_para_download(arquivo: Arquivo) -> Path:
    """Resolve e valida o caminho físico do arquivo para download.

    Args:
        arquivo: Instância de ``Arquivo`` com o caminho armazenado.

    Returns:
        O ``Path`` do arquivo físico existente.

    Raises:
        HTTPException: 404 quando o arquivo físico não existe no servidor.
    """
    caminho = Path(arquivo.caminho_arquivo)
    # Confere se o caminho aponta para um arquivo regular existente.
    if not caminho.is_file():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Arquivo físico não encontrado no servidor",
        )
    return caminho


def deletar_arquivo(db: Session, arquivo: Arquivo) -> None:
    """Remove o registro do banco e o arquivo físico correspondente.

    Args:
        db: Sessão do SQLAlchemy.
        arquivo: Instância de ``Arquivo`` a ser removida.

    Returns:
        ``None``.

    Raises:
        Erros de banco são propagados; a remoção do arquivo físico ignora
        ausência do mesmo (``missing_ok=True``).
    """
    caminho = Path(arquivo.caminho_arquivo)
    # Remove primeiro o registro; só apaga do disco após o commit bem-sucedido.
    db.delete(arquivo)
    db.commit()
    caminho.unlink(missing_ok=True)
