"""Serviço de categorias e pastas da biblioteca.

Cuida do CRUD de categorias (com unicidade de nome e bloqueio de exclusão
quando há arquivos vinculados) e do CRUD de pastas (com validação de pasta
pai, prevenção de auto-referência e bloqueio de exclusão com conteúdo).
"""

from pathlib import Path

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.model.categoria import Categoria, Pasta
from app.schemas.categoria_schema import CategoriaCreate, PastaCreate
from app.services.common_service import montar_pagina, paginar


def obter_categoria(db: Session, categoria_id: int) -> Categoria | None:
    """Busca uma categoria pelo ID.

    Args:
        db: Sessão do SQLAlchemy.
        categoria_id: Identificador primário da categoria.

    Returns:
        A categoria encontrada ou ``None``.

    Raises:
        Nenhuma exceção de negócio; erros de banco são propagados.
    """
    return db.get(Categoria, categoria_id)


def listar_categorias(db: Session, skip: int = 0, limit: int = 100, busca: str | None = None):
    """Lista categorias com busca opcional e paginação.

    Args:
        db: Sessão do SQLAlchemy.
        skip: Offset da paginação.
        limit: Máximo de categorias retornadas.
        busca: Texto parcial pesquisado em nome e descrição.

    Returns:
        Um objeto ``Page`` com as categorias e o total filtrado.

    Raises:
        Nenhuma exceção de negócio; erros de banco são propagados.
    """
    query = db.query(Categoria)
    if busca:
        termo = f"%{busca}%"
        # Casa o termo no nome OU na descrição, sem diferenciar maiúsculas.
        query = query.filter(Categoria.nome.ilike(termo) | Categoria.descricao.ilike(termo))
    # Ordena alfabeticamente pelo nome.
    query = query.order_by(Categoria.nome)
    items, total = paginar(query, skip, limit)
    return montar_pagina(items, total, skip, limit)


def criar_categoria(db: Session, dados: CategoriaCreate) -> Categoria:
    """Cria uma nova categoria garantindo nome único.

    Args:
        db: Sessão do SQLAlchemy.
        dados: Dados de criação da categoria.

    Returns:
        A categoria persistida e recarregada do banco.

    Raises:
        HTTPException: 409 quando já existe uma categoria com o mesmo nome.
    """
    # Verifica duplicidade pelo nome exato antes de inserir.
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
    """Atualiza parcialmente uma categoria, validando unicidade do nome.

    Args:
        db: Sessão do SQLAlchemy.
        categoria: Categoria já carregada que será modificada.
        dados: Campos a alterar.

    Returns:
        A categoria atualizada e recarregada do banco.

    Raises:
        HTTPException: 409 quando o novo nome já pertence a outra categoria.
    """
    novo_nome = dados.get("nome")
    # Só valida unicidade se o nome foi informado e realmente mudou.
    if novo_nome and novo_nome != categoria.nome:
        existente = db.query(Categoria).filter(Categoria.nome == novo_nome).first()
        # Ignora a própria categoria (mesmo ID) ao checar conflito.
        if existente and existente.id != categoria.id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Já existe uma categoria com este nome",
            )
    # Aplica os campos recebidos dinamicamente.
    for campo, valor in dados.items():
        setattr(categoria, campo, valor)
    db.commit()
    db.refresh(categoria)
    return categoria


def deletar_categoria(db: Session, categoria: Categoria) -> None:
    """Exclui uma categoria se não houver arquivos vinculados.

    Args:
        db: Sessão do SQLAlchemy.
        categoria: Categoria a ser removida.

    Returns:
        ``None``.

    Raises:
        HTTPException: 409 quando existem arquivos vinculados à categoria.
    """
    # O relacionamento ``arquivos`` é carregado para impedir exclusão em uso.
    if categoria.arquivos:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Não é possível excluir uma categoria com arquivos vinculados",
        )
    db.delete(categoria)
    db.commit()


def obter_pasta(db: Session, pasta_id: int) -> Pasta | None:
    """Busca uma pasta pelo ID.

    Args:
        db: Sessão do SQLAlchemy.
        pasta_id: Identificador primário da pasta.

    Returns:
        A pasta encontrada ou ``None``.

    Raises:
        Nenhuma exceção de negócio; erros de banco são propagados.
    """
    return db.get(Pasta, pasta_id)


def listar_pastas(db: Session, skip: int = 0, limit: int = 100, busca: str | None = None):
    """Lista pastas com busca opcional e paginação.

    Args:
        db: Sessão do SQLAlchemy.
        skip: Offset da paginação.
        limit: Máximo de pastas retornadas.
        busca: Texto parcial pesquisado no nome.

    Returns:
        Um objeto ``Page`` com as pastas e o total filtrado.

    Raises:
        Nenhuma exceção de negócio; erros de banco são propagados.
    """
    query = db.query(Pasta)
    if busca:
        query = query.filter(Pasta.nome.ilike(f"%{busca}%"))
    query = query.order_by(Pasta.nome)
    items, total = paginar(query, skip, limit)
    return montar_pagina(items, total, skip, limit)


def criar_pasta(db: Session, dados: PastaCreate) -> Pasta:
    """Cria uma nova pasta, validando a existência da pasta pai.

    Args:
        db: Sessão do SQLAlchemy.
        dados: Dados de criação da pasta.

    Returns:
        A pasta persistida e recarregada do banco.

    Raises:
        HTTPException: 404 quando a pasta pai informada não existe.
    """
    # A pasta pai é opcional; se informada, precisa existir.
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
    """Atualiza parcialmente uma pasta, validando a pasta pai.

    Args:
        db: Sessão do SQLAlchemy.
        pasta: Pasta já carregada que será modificada.
        dados: Campos a alterar.

    Returns:
        A pasta atualizada e recarregada do banco.

    Raises:
        HTTPException: 400 quando a pasta tenta ser pai de si mesma e 404
            quando a pasta pai informada não existe.
    """
    # Só valida a hierarquia se uma nova pasta pai foi informada.
    if dados.get("pasta_pai_id") is not None:
        # Impede auto-referência direta.
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
    """Exclui uma pasta se não houver arquivos nem subpastas.

    Args:
        db: Sessão do SQLAlchemy.
        pasta: Pasta a ser removida.

    Returns:
        ``None``.

    Raises:
        HTTPException: 409 quando a pasta possui arquivos ou subpastas.
    """
    # Protege a integridade da árvore de pastas.
    if pasta.arquivos or pasta.subpastas:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Não é possível excluir uma pasta com arquivos ou subpastas",
        )
    db.delete(pasta)
    db.commit()
