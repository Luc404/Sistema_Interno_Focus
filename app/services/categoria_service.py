from pathlib import Path

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.model.categoria import Categoria, Pasta
from app.schemas.categoria_schema import CategoriaCreate, PastaCreate
from app.services.common_service import montar_pagina, paginar


def obter_categoria(db: Session, categoria_id: int) -> Categoria | None:
    return db.get(Categoria, categoria_id)


def listar_categorias(db: Session, skip: int = 0, limit: int = 100, busca: str | None = None):
    query = db.query(Categoria)
    if busca:
        termo = f"%{busca}%"
        query = query.filter(Categoria.nome.ilike(termo) | Categoria.descricao.ilike(termo))
    query = query.order_by(Categoria.nome)
    items, total = paginar(query, skip, limit)
    return montar_pagina(items, total, skip, limit)


def criar_categoria(db: Session, dados: CategoriaCreate) -> Categoria:
    if db.query(Categoria).filter(Categoria.nome == dados.nome).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Já existe uma categoria com este nome",
        )
    categoria = Categoria(nome=dados.nome, descricao=dados.descricao)
    db.add(categoria)
    db.commit()
    db.refresh(categoria)
    return categoria


def atualizar_categoria(db: Session, categoria: Categoria, dados: dict) -> Categoria:
    novo_nome = dados.get("nome")
    if novo_nome and novo_nome != categoria.nome:
        existente = db.query(Categoria).filter(Categoria.nome == novo_nome).first()
        if existente and existente.id != categoria.id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Já existe uma categoria com este nome",
            )
    for campo, valor in dados.items():
        setattr(categoria, campo, valor)
    db.commit()
    db.refresh(categoria)
    return categoria


def deletar_categoria(db: Session, categoria: Categoria) -> None:
    if categoria.arquivos:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Não é possível excluir uma categoria com arquivos vinculados",
        )
    db.delete(categoria)
    db.commit()


def obter_pasta(db: Session, pasta_id: int) -> Pasta | None:
    return db.get(Pasta, pasta_id)


def listar_pastas(db: Session, skip: int = 0, limit: int = 100, busca: str | None = None):
    query = db.query(Pasta)
    if busca:
        query = query.filter(Pasta.nome.ilike(f"%{busca}%"))
    query = query.order_by(Pasta.nome)
    items, total = paginar(query, skip, limit)
    return montar_pagina(items, total, skip, limit)


def criar_pasta(db: Session, dados: PastaCreate) -> Pasta:
    if dados.pasta_pai_id is not None and not obter_pasta(db, dados.pasta_pai_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pasta pai não encontrada")
    pasta = Pasta(
        nome=dados.nome,
        descricao=dados.descricao,
        pasta_pai_id=dados.pasta_pai_id,
    )
    db.add(pasta)
    db.commit()
    db.refresh(pasta)
    return pasta


def atualizar_pasta(db: Session, pasta: Pasta, dados: dict) -> Pasta:
    if dados.get("pasta_pai_id") is not None:
        if dados["pasta_pai_id"] == pasta.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Uma pasta não pode ser pai dela mesma",
            )
        if not obter_pasta(db, dados["pasta_pai_id"]):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pasta pai não encontrada")
    for campo, valor in dados.items():
        setattr(pasta, campo, valor)
    db.commit()
    db.refresh(pasta)
    return pasta


def deletar_pasta(db: Session, pasta: Pasta) -> None:
    if pasta.arquivos or pasta.subpastas:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Não é possível excluir uma pasta com arquivos ou subpastas",
        )
    db.delete(pasta)
    db.commit()
