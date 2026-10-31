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
    query = db.query(Arquivo)
    if busca:
        query = query.filter(Arquivo.titulo.ilike(f"%{busca}%"))
    if categoria:
        query = query.filter(Arquivo.categoria == categoria)
    if categoria_id is not None:
        query = query.filter(Arquivo.categoria_id == categoria_id)
    if pasta_id is not None:
        query = query.filter(Arquivo.pasta_id == pasta_id)
    if usuario_id is not None:
        query = query.filter(Arquivo.usuario_id == usuario_id)

    query = query.order_by(Arquivo.data_upload.desc())
    items, total = paginar(query, skip, limit)
    return montar_pagina(items, total, skip, limit)


def _validar_categoria_pasta(db: Session, categoria_id: int | None, pasta_id: int | None) -> None:
    if categoria_id is not None and not db.get(Categoria, categoria_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Categoria não encontrada")
    if pasta_id is not None and not db.get(Pasta, pasta_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pasta não encontrada")


def criar_arquivo(db: Session, arquivo_dto: ArquivoCreate, usuario_id: int) -> Arquivo:
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
    settings = get_settings()
    _validar_categoria_pasta(db, categoria_id, pasta_id)

    if not upload.filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Arquivo sem nome")

    extensao = Path(upload.filename).suffix.lower()
    nome_seguro = f"{uuid4().hex}{extensao}"
    destino = settings.upload_path / nome_seguro

    tamanho = 0
    try:
        with destino.open("wb") as saida:
            while chunk := upload.file.read(1024 * 1024):
                tamanho += len(chunk)
                if tamanho > settings.max_upload_size_bytes:
                    raise HTTPException(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        detail=f"O arquivo excede o limite de {settings.max_upload_size_mb} MB",
                    )
                saida.write(chunk)
    except Exception:
        destino.unlink(missing_ok=True)
        raise

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
    if "categoria_id" in dados or "pasta_id" in dados:
        _validar_categoria_pasta(
            db,
            dados.get("categoria_id", arquivo.categoria_id),
            dados.get("pasta_id", arquivo.pasta_id),
        )
    for campo, valor in dados.items():
        setattr(arquivo, campo, valor)
    db.commit()
    db.refresh(arquivo)
    return arquivo


def caminho_para_download(arquivo: Arquivo) -> Path:
    caminho = Path(arquivo.caminho_arquivo)
    if not caminho.is_file():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Arquivo físico não encontrado no servidor",
        )
    return caminho


def deletar_arquivo(db: Session, arquivo: Arquivo) -> None:
    caminho = Path(arquivo.caminho_arquivo)
    db.delete(arquivo)
    db.commit()
    caminho.unlink(missing_ok=True)
