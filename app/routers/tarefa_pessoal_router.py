"""Router de tarefas pessoais da agenda.

Permite criar, listar (as próprias ou de outro usuário, com permissão),
consultar, atualizar, alterar status e excluir tarefas pessoais. Cada tarefa
pertence ao usuário informado no token ou ao usuário consultado.

Endpoints expostos (prefixo ``/api/tarefas-pessoais``):
- ``POST /``                         -> cria tarefa;
- ``GET /minhas``                    -> lista tarefas do usuário autenticado;
- ``GET /usuario/{usuario_id}``      -> lista tarefas de outro usuário (dono/ADMIN);
- ``GET /{tarefa_id}``               -> consulta tarefa;
- ``PATCH /{tarefa_id}``             -> atualização parcial;
- ``PATCH /{tarefa_id}/status``      -> altera somente o status;
- ``DELETE /{tarefa_id}``            -> exclusão.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.deps import ensure_owner_or_admin, get_current_user, require_perfis
from app.database import get_db
from app.model.usuario import Usuario
from app.schemas.common import Mensagem, Page
from app.schemas.tarefa_pessoal_schema import (
    TarefaPessoalCreate,
    TarefaPessoalResponse,
    TarefaPessoalUpdate,
    TarefaStatusUpdate,
)
from app.services import tarefa_pessoal_service

# Prefixo e tag OpenAPI das rotas de tarefas pessoais.
router = APIRouter(prefix="/api/tarefas-pessoais", tags=["Agenda - Tarefas Pessoais"])


@router.post("/", response_model=TarefaPessoalResponse, status_code=status.HTTP_201_CREATED)
def criar_tarefa(
    tarefa: TarefaPessoalCreate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    """Cria uma tarefa pessoal para o usuário autenticado.

    Autenticação: obrigatória; o dono é definido pelo token.
    Retorno: ``TarefaPessoalResponse`` criada (HTTP 201).
    """
    return tarefa_pessoal_service.criar_tarefa(db=db, tarefa=tarefa, usuario_id=usuario.id)


@router.get("/minhas", response_model=Page[TarefaPessoalResponse])
def listar_minhas_tarefas(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    busca: str | None = None,
    status_tarefa: str | None = Query(None, alias="status"),
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    """Lista as tarefas pessoais do usuário autenticado.

    ``skip``/``limit`` controlam a paginação (máximo de 500 por página).
    O filtro de status é exposto como query ``status`` via ``alias``.

    Autenticação: obrigatória; o resultado é restrito ao próprio usuário.
    Retorno: ``Page[TarefaPessoalResponse]``.
    """
    return tarefa_pessoal_service.listar_tarefas_por_usuario(
        db=db,
        usuario_id=usuario.id,
        skip=skip,
        limit=limit,
        busca=busca,
        status_tarefa=status_tarefa,
    )


@router.get("/usuario/{usuario_id}", response_model=Page[TarefaPessoalResponse])
def listar_tarefas_usuario(
    usuario_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    busca: str | None = None,
    status_tarefa: str | None = Query(None, alias="status"),
    db: Session = Depends(get_db),
    atual: Usuario = Depends(get_current_user),
):
    """Lista as tarefas pessoais de um usuário específico.

    ``skip``/``limit`` controlam a paginação (máximo de 500 por página).
    Autenticação/permissão: somente o próprio usuário ou ADMIN.
    Retorno: ``Page[TarefaPessoalResponse]``.
    """
    # Impede que um usuário consulte as tarefas de outro sem ser ADMIN.
    ensure_owner_or_admin(atual, usuario_id)
    return tarefa_pessoal_service.listar_tarefas_por_usuario(
        db=db,
        usuario_id=usuario_id,
        skip=skip,
        limit=limit,
        busca=busca,
        status_tarefa=status_tarefa,
    )


@router.get("/{tarefa_id}", response_model=TarefaPessoalResponse)
def obter_tarefa(
    tarefa_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    """Consulta uma tarefa pessoal pelo identificador.

    Autenticação/permissão: somente o dono da tarefa ou ADMIN.
    Retorno: ``TarefaPessoalResponse`` ou HTTP 404 se não existir.
    """
    db_tarefa = tarefa_pessoal_service.obter_tarefa_por_id(db=db, tarefa_id=tarefa_id)
    if not db_tarefa:
        raise HTTPException(status_code=404, detail="Tarefa não encontrada")
    ensure_owner_or_admin(usuario, db_tarefa.usuario_id)
    return db_tarefa


@router.patch("/{tarefa_id}", response_model=TarefaPessoalResponse)
def atualizar_tarefa(
    tarefa_id: int,
    dados: TarefaPessoalUpdate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    """Atualiza parcialmente uma tarefa pessoal.

    Apenas campos enviados são aplicados (``exclude_unset=True``).
    Autenticação/permissão: somente o dono da tarefa ou ADMIN.
    Retorno: ``TarefaPessoalResponse`` atualizada; HTTP 404 se não existir.
    """
    db_tarefa = tarefa_pessoal_service.obter_tarefa_por_id(db=db, tarefa_id=tarefa_id)
    if not db_tarefa:
        raise HTTPException(status_code=404, detail="Tarefa não encontrada")
    ensure_owner_or_admin(usuario, db_tarefa.usuario_id)
    return tarefa_pessoal_service.atualizar_tarefa(
        db, db_tarefa, dados.model_dump(exclude_unset=True)
    )


@router.patch("/{tarefa_id}/status", response_model=TarefaPessoalResponse)
def alterar_status_tarefa(
    tarefa_id: int,
    dados: TarefaStatusUpdate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    """Altera somente o status de uma tarefa pessoal.

    Autenticação/permissão: somente o dono da tarefa ou ADMIN.
    Retorno: ``TarefaPessoalResponse`` com o novo status.
    """
    db_tarefa = tarefa_pessoal_service.obter_tarefa_por_id(db=db, tarefa_id=tarefa_id)
    if not db_tarefa:
        raise HTTPException(status_code=404, detail="Tarefa não encontrada")
    ensure_owner_or_admin(usuario, db_tarefa.usuario_id)
    return tarefa_pessoal_service.mudar_status(db, db_tarefa, dados.status)


@router.delete("/{tarefa_id}", response_model=Mensagem)
def deletar_tarefa(
    tarefa_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    """Exclui uma tarefa pessoal.

    Autenticação/permissão: somente o dono da tarefa ou ADMIN.
    Retorno: ``Mensagem`` de confirmação; HTTP 404 se não existir.
    """
    db_tarefa = tarefa_pessoal_service.obter_tarefa_por_id(db=db, tarefa_id=tarefa_id)
    if not db_tarefa:
        raise HTTPException(status_code=404, detail="Tarefa não encontrada")
    ensure_owner_or_admin(usuario, db_tarefa.usuario_id)
    tarefa_pessoal_service.deletar_tarefa(db, db_tarefa)
    return Mensagem(mensagem="Tarefa excluída com sucesso")
