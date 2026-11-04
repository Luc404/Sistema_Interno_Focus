"""Serviço de notebooks (anotações).

Implementa listagem com busca em título/subtítulo/conteúdo/tags, filtros por
grupo e autor, além do CRUD básico de notebooks.
"""

from sqlalchemy.orm import Session

from app.model.notebook import Notebook
from app.schemas.notebook_schema import NotebookCreate
from app.services.common_service import montar_pagina, paginar


def obter_notebook(db: Session, notebook_id: int) -> Notebook | None:
    """Busca um notebook pelo ID.

    Args:
        db: Sessão do SQLAlchemy.
        notebook_id: Identificador primário do notebook.

    Returns:
        O notebook encontrado ou ``None``.

    Raises:
        Nenhuma exceção de negócio; erros de banco são propagados.
    """
    return db.get(Notebook, notebook_id)


def listar_notebooks(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    busca: str | None = None,
    grupo: str | None = None,
    autor_id: int | None = None,
):
    """Lista notebooks com busca textual, filtros e paginação.

    Args:
        db: Sessão do SQLAlchemy.
        skip: Offset da paginação.
        limit: Máximo de notebooks retornados.
        busca: Texto parcial pesquisado em título, subtítulo, conteúdo e tags.
        grupo: Grupo exato do notebook.
        autor_id: ID do autor do notebook.

    Returns:
        Um objeto ``Page`` com os notebooks e o total filtrado.

    Raises:
        Nenhuma exceção de negócio; erros de banco são propagados.
    """
    query = db.query(Notebook)
    if busca:
        termo = f"%{busca}%"
        # OR entre os quatro campos pesquisáveis do notebook.
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

    # Mais recentemente atualizados primeiro.
    query = query.order_by(Notebook.data_atualizacao.desc())
    items, total = paginar(query, skip, limit)
    return montar_pagina(items, total, skip, limit)


def criar_notebook(db: Session, dados: NotebookCreate, autor_id: int) -> Notebook:
    """Cria um novo notebook para o autor informado.

    Args:
        db: Sessão do SQLAlchemy.
        dados: Dados de criação do notebook.
        autor_id: ID do usuário autor.

    Returns:
        O notebook persistido e recarregado do banco.

    Raises:
        Erros de banco são propagados.
    """
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
    """Atualiza parcialmente um notebook.

    Args:
        db: Sessão do SQLAlchemy.
        notebook: Notebook já carregado que será modificado.
        dados: Campos a alterar.

    Returns:
        O notebook atualizado e recarregado do banco.

    Raises:
        Erros de banco são propagados.
    """
    # Aplica dinamicamente os campos recebidos.
    for campo, valor in dados.items():
        setattr(notebook, campo, valor)
    db.commit()
    db.refresh(notebook)
    return notebook


def deletar_notebook(db: Session, notebook: Notebook) -> None:
    """Remove um notebook do banco.

    Args:
        db: Sessão do SQLAlchemy.
        notebook: Notebook a ser removido.

    Returns:
        ``None``.

    Raises:
        Erros de banco são propagados.
    """
    db.delete(notebook)
    db.commit()
