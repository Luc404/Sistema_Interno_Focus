from sqlalchemy.orm import Session

from app.model.notebook import Notebook
from app.schemas.notebook_schema import NotebookCreate
from app.services.common_service import montar_pagina, paginar


def obter_notebook(db: Session, notebook_id: int) -> Notebook | None:
    return db.get(Notebook, notebook_id)


def listar_notebooks(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    busca: str | None = None,
    grupo: str | None = None,
    autor_id: int | None = None,
):
    query = db.query(Notebook)
    if busca:
        termo = f"%{busca}%"
        query = query.filter(
            Notebook.titulo.ilike(termo)
            | Notebook.subtitulo.ilike(termo)
            | Notebook.conteudo.ilike(termo)
            | Notebook.tags.ilike(termo)
        )
    if grupo:
        query = query.filter(Notebook.grupo == grupo)
    if autor_id is not None:
        query = query.filter(Notebook.autor_id == autor_id)

    query = query.order_by(Notebook.data_atualizacao.desc())
    items, total = paginar(query, skip, limit)
    return montar_pagina(items, total, skip, limit)


def criar_notebook(db: Session, dados: NotebookCreate, autor_id: int) -> Notebook:
    notebook = Notebook(
        grupo=dados.grupo,
        titulo=dados.titulo,
        subtitulo=dados.subtitulo,
        conteudo=dados.conteudo,
        tags=dados.tags,
        autor_id=autor_id,
    )
    db.add(notebook)
    db.commit()
    db.refresh(notebook)
    return notebook


def atualizar_notebook(db: Session, notebook: Notebook, dados: dict) -> Notebook:
    for campo, valor in dados.items():
        setattr(notebook, campo, valor)
    db.commit()
    db.refresh(notebook)
    return notebook


def deletar_notebook(db: Session, notebook: Notebook) -> None:
    db.delete(notebook)
    db.commit()
