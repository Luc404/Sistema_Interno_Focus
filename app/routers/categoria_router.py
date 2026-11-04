"""Routers da biblioteca de categorias e pastas.

Define dois roteadores no mesmo módulo: ``/api/categorias`` para categorias e
``/api/pastas`` para pastas da biblioteca. Operações de escrita exigem perfil
ADMIN; operações de leitura exigem usuário autenticado.

Endpoints de categorias (prefixo ``/api/categorias``):
- ``POST /``, ``GET /``, ``GET /{categoria_id}``, ``PATCH /{categoria_id}``,
  ``DELETE /{categoria_id}``.

Endpoints de pastas (prefixo ``/api/pastas``):
- ``POST /``, ``GET /``, ``GET /{pasta_id}``, ``PATCH /{pasta_id}``,
  ``DELETE /{pasta_id}``.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, require_perfis
from app.database import get_db
from app.model.usuario import Usuario
from app.schemas.categoria_schema import (
    CategoriaCreate,
    CategoriaResponse,
    CategoriaUpdate,
    PastaCreate,
    PastaResponse,
    PastaUpdate,
)
from app.schemas.common import Mensagem, Page
from app.services import categoria_service

# Roteador de categorias e roteador separado de pastas (prefixos distintos).
router = APIRouter(prefix="/api/categorias", tags=["Biblioteca - Categorias"])
pasta_router = APIRouter(prefix="/api/pastas", tags=["Biblioteca - Pastas"])


@router.post("/", response_model=CategoriaResponse, status_code=status.HTTP_201_CREATED)
def criar_categoria(
    dados: CategoriaCreate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_perfis("ADMIN")),
):
    """Cria uma nova categoria da biblioteca.

    Autenticação/permissão: exige perfil ADMIN.
    Retorno: ``CategoriaResponse`` criada (HTTP 201).
    """
    return categoria_service.criar_categoria(db, dados)


@router.get("/", response_model=Page[CategoriaResponse])
def listar_categorias(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    busca: str | None = None,
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    """Lista categorias com paginação e busca opcional.

    ``skip``/``limit`` controlam a paginação (máximo de 500 por página).
    Autenticação: qualquer usuário autenticado.
    Retorno: ``Page[CategoriaResponse]``.
    """
    return categoria_service.listar_categorias(db, skip, limit, busca)


@router.get("/{categoria_id}", response_model=CategoriaResponse)
def obter_categoria(
    categoria_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    """Consulta uma categoria pelo identificador.

    Autenticação: qualquer usuário autenticado.
    Retorno: ``CategoriaResponse`` ou HTTP 404 se não existir.
    """
    categoria = categoria_service.obter_categoria(db, categoria_id)
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoria não encontrada")
    return categoria


@router.patch("/{categoria_id}", response_model=CategoriaResponse)
def atualizar_categoria(
    categoria_id: int,
    dados: CategoriaUpdate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_perfis("ADMIN")),
):
    """Atualiza parcialmente uma categoria.

    Apenas campos enviados são aplicados (``exclude_unset=True``).
    Autenticação/permissão: exige perfil ADMIN.
    Retorno: ``CategoriaResponse`` atualizada; HTTP 404 se não existir.
    """
    categoria = categoria_service.obter_categoria(db, categoria_id)
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoria não encontrada")
    return categoria_service.atualizar_categoria(
        db, categoria, dados.model_dump(exclude_unset=True)
    )


@router.delete("/{categoria_id}", response_model=Mensagem)
def deletar_categoria(
    categoria_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_perfis("ADMIN")),
):
    """Exclui uma categoria.

    Autenticação/permissão: exige perfil ADMIN.
    Retorno: ``Mensagem`` de confirmação; HTTP 404 se não existir.
    """
    categoria = categoria_service.obter_categoria(db, categoria_id)
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoria não encontrada")
    categoria_service.deletar_categoria(db, categoria)
    return Mensagem(mensagem="Categoria excluída com sucesso")


# As rotas de pasta abaixo usam o `pasta_router` (prefixo /api/pastas).
@pasta_router.post("/", response_model=PastaResponse, status_code=status.HTTP_201_CREATED)
def criar_pasta(
    dados: PastaCreate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_perfis("ADMIN")),
):
    """Cria uma nova pasta da biblioteca.

    Autenticação/permissão: exige perfil ADMIN.
    Retorno: ``PastaResponse`` criada (HTTP 201).
    """
    return categoria_service.criar_pasta(db, dados)


@pasta_router.get("/", response_model=Page[PastaResponse])
def listar_pastas(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    busca: str | None = None,
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    """Lista pastas com paginação e busca opcional.

    ``skip``/``limit`` controlam a paginação (máximo de 500 por página).
    Autenticação: qualquer usuário autenticado.
    Retorno: ``Page[PastaResponse]``.
    """
    return categoria_service.listar_pastas(db, skip, limit, busca)


@pasta_router.get("/{pasta_id}", response_model=PastaResponse)
def obter_pasta(
    pasta_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    """Consulta uma pasta pelo identificador.

    Autenticação: qualquer usuário autenticado.
    Retorno: ``PastaResponse`` ou HTTP 404 se não existir.
    """
    pasta = categoria_service.obter_pasta(db, pasta_id)
    if not pasta:
        raise HTTPException(status_code=404, detail="Pasta não encontrada")
    return pasta


@pasta_router.patch("/{pasta_id}", response_model=PastaResponse)
def atualizar_pasta(
    pasta_id: int,
    dados: PastaUpdate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_perfis("ADMIN")),
):
    """Atualiza parcialmente uma pasta.

    Apenas campos enviados são aplicados (``exclude_unset=True``).
    Autenticação/permissão: exige perfil ADMIN.
    Retorno: ``PastaResponse`` atualizada; HTTP 404 se não existir.
    """
    pasta = categoria_service.obter_pasta(db, pasta_id)
    if not pasta:
        raise HTTPException(status_code=404, detail="Pasta não encontrada")
    return categoria_service.atualizar_pasta(db, pasta, dados.model_dump(exclude_unset=True))


@pasta_router.delete("/{pasta_id}", response_model=Mensagem)
def deletar_pasta(
    pasta_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_perfis("ADMIN")),
):
    """Exclui uma pasta.

    Autenticação/permissão: exige perfil ADMIN.
    Retorno: ``Mensagem`` de confirmação; HTTP 404 se não existir.
    """
    pasta = categoria_service.obter_pasta(db, pasta_id)
    if not pasta:
        raise HTTPException(status_code=404, detail="Pasta não encontrada")
    categoria_service.deletar_pasta(db, pasta)
    return Mensagem(mensagem="Pasta excluída com sucesso")
