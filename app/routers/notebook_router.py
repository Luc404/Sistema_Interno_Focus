"""Router de notebooks (anotações).

Permite criar, listar com filtros, consultar, atualizar e excluir notebooks de
anotações. Cada notebook pertence ao usuário que o criou (``autor_id``).

Endpoints expostos (prefixo ``/api/notebooks``):
- ``POST /``              -> cria notebook;
- ``GET /``               -> listagem paginada com filtros;
- ``GET /{notebook_id}``  -> consulta notebook;
- ``PATCH /{notebook_id}``-> atualização parcial;
- ``DELETE /{notebook_id}``-> exclusão.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.deps import ensure_owner_or_admin, get_current_user
from app.database import get_db
from app.model.usuario import Usuario
from app.schemas.common import Mensagem, Page
from app.schemas.notebook_schema import NotebookCreate, NotebookResponse, NotebookUpdate
from app.services import notebook_service

# Prefixo e tag OpenAPI das rotas de notebooks.
router = APIRouter(prefix="/api/notebooks", tags=["Notebooks"])


@router.post("/", response_model=NotebookResponse, status_code=status.HTTP_201_CREATED)
def criar_notebook(
    dados: NotebookCreate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    """Cria um novo notebook associado ao usuário autenticado.

    Autenticação: obrigatória; o autor é definido pelo token.
    Retorno: ``NotebookResponse`` criado (HTTP 201).
    """
    return notebook_service.criar_notebook(db, dados, usuario.id)


@router.get("/", response_model=Page[NotebookResponse])
def listar_notebooks(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    busca: str | None = None,
    grupo: str | None = None,
    autor_id: int | None = None,
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    """Lista notebooks com paginação e filtros opcionais.

    ``skip``/``limit`` controlam a paginação (máximo de 500 por página).
    Autenticação: obrigatória.
    Retorno: ``Page[NotebookResponse]`` com total e itens da página.
    """
    return notebook_service.listar_notebooks(
        db, skip=skip, limit=limit, busca=busca, grupo=grupo, autor_id=autor_id
    )


@router.get("/{notebook_id}", response_model=NotebookResponse)
def obter_notebook(
    notebook_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    """Consulta um notebook pelo identificador.

    Autenticação: obrigatória.
    Retorno: ``NotebookResponse`` ou HTTP 404 se não existir.
    """
    notebook = notebook_service.obter_notebook(db, notebook_id)
    if not notebook:
        raise HTTPException(status_code=404, detail="Notebook não encontrado")
    return notebook


@router.patch("/{notebook_id}", response_model=NotebookResponse)
def atualizar_notebook(
    notebook_id: int,
    dados: NotebookUpdate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    """Atualiza parcialmente um notebook.

    Apenas campos enviados são aplicados (``exclude_unset=True``).
    Autenticação/permissão: somente o autor do notebook ou ADMIN.
    Retorno: ``NotebookResponse`` atualizado; HTTP 404 se não existir.
    """
    notebook = notebook_service.obter_notebook(db, notebook_id)
    if not notebook:
        raise HTTPException(status_code=404, detail="Notebook não encontrado")
    # Garante que o usuário seja o autor do notebook ou administrador.
    ensure_owner_or_admin(usuario, notebook.autor_id)
    return notebook_service.atualizar_notebook(
        db, notebook, dados.model_dump(exclude_unset=True)
    )


@router.delete("/{notebook_id}", response_model=Mensagem)
def deletar_notebook(
    notebook_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    """Exclui um notebook.

    Autenticação/permissão: somente o autor do notebook ou ADMIN.
    Retorno: ``Mensagem`` de confirmação; HTTP 404 se não existir.
    """
    notebook = notebook_service.obter_notebook(db, notebook_id)
    if not notebook:
        raise HTTPException(status_code=404, detail="Notebook não encontrado")
    ensure_owner_or_admin(usuario, notebook.autor_id)
    notebook_service.deletar_notebook(db, notebook)
    return Mensagem(mensagem="Notebook excluído com sucesso")
