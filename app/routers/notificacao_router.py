"""Router de notificações.

Permite que administradores criem notificações e que cada usuário consulte e
gerencie as suas próprias notificações (listar, marcar como lida, excluir).

Endpoints expostos (prefixo ``/api/notificacoes``):
- ``POST /``                    -> cria notificação (ADMIN);
- ``GET /minhas``               -> lista notificações do usuário autenticado;
- ``PATCH /ler-todas``          -> marca todas as notificações como lidas;
- ``GET /{notificacao_id}``     -> consulta notificação própria;
- ``PATCH /{notificacao_id}/ler`` -> marca uma notificação como lida;
- ``DELETE /{notificacao_id}``  -> exclui notificação própria.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, require_perfis
from app.database import get_db
from app.model.usuario import Usuario
from app.schemas.common import Mensagem, Page
from app.schemas.notificacao_schema import NotificacaoCreate, NotificacaoResponse
from app.services import notificacao_service

# Prefixo e tag OpenAPI das rotas de notificações.
router = APIRouter(prefix="/api/notificacoes", tags=["Notificações"])


@router.post("/", response_model=NotificacaoResponse, status_code=status.HTTP_201_CREATED)
def criar_notificacao(
    dados: NotificacaoCreate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_perfis("ADMIN")),
):
    """Cria uma notificação para destinatário(s) definidos no payload.

    Autenticação/permissão: exige perfil ADMIN.
    Retorno: ``NotificacaoResponse`` criada (HTTP 201).
    """
    return notificacao_service.criar_notificacao(db, dados)


@router.get("/minhas", response_model=Page[NotificacaoResponse])
def listar_minhas_notificacoes(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    lida: bool | None = None,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    """Lista as notificações do usuário autenticado.

    ``skip``/``limit`` controlam a paginação (máximo de 500 por página).
    O filtro ``lida`` permite trazer apenas lidas (``true``) ou não lidas
    (``false``); omitido, traz ambas.

    Autenticação: obrigatória; o ``usuario.id`` limita o resultado ao dono.
    Retorno: ``Page[NotificacaoResponse]``.
    """
    return notificacao_service.listar_notificacoes(
        db, usuario.id, skip=skip, limit=limit, lida=lida
    )


@router.patch("/ler-todas", response_model=Mensagem)
def marcar_todas_como_lidas(
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    """Marca todas as notificações do usuário autenticado como lidas.

    Autenticação: obrigatória.
    Retorno: ``Mensagem`` informando a quantidade de notificações atualizadas.
    """
    # A quantidade retornada pelo serviço é usada na mensagem de confirmação.
    quantidade = notificacao_service.marcar_todas_lidas(db, usuario.id)
    return Mensagem(mensagem=f"{quantidade} notificação(ões) marcada(s) como lida(s)")


@router.get("/{notificacao_id}", response_model=NotificacaoResponse)
def obter_notificacao(
    notificacao_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    """Consulta uma notificação do próprio usuário.

    Autenticação/permissão: obrigatória; valida que a notificação pertence ao
    usuário autenticado.
    Retorno: ``NotificacaoResponse``; HTTP 404 se não existir.
    """
    notificacao = notificacao_service.obter_notificacao(db, notificacao_id)
    if not notificacao:
        raise HTTPException(status_code=404, detail="Notificação não encontrada")
    # Impede acesso a notificações de outros usuários.
    notificacao_service.validar_proprietario(notificacao, usuario.id)
    return notificacao


@router.patch("/{notificacao_id}/ler", response_model=NotificacaoResponse)
def marcar_como_lida(
    notificacao_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    """Marca uma notificação específica como lida.

    Autenticação/permissão: obrigatória; valida a propriedade da notificação.
    Retorno: ``NotificacaoResponse`` atualizada; HTTP 404 se não existir.
    """
    notificacao = notificacao_service.obter_notificacao(db, notificacao_id)
    if not notificacao:
        raise HTTPException(status_code=404, detail="Notificação não encontrada")
    notificacao_service.validar_proprietario(notificacao, usuario.id)
    return notificacao_service.marcar_lida(db, notificacao)


@router.delete("/{notificacao_id}", response_model=Mensagem)
def deletar_notificacao(
    notificacao_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    """Exclui uma notificação do próprio usuário.

    Autenticação/permissão: obrigatória; valida a propriedade da notificação.
    Retorno: ``Mensagem`` de confirmação; HTTP 404 se não existir.
    """
    notificacao = notificacao_service.obter_notificacao(db, notificacao_id)
    if not notificacao:
        raise HTTPException(status_code=404, detail="Notificação não encontrada")
    notificacao_service.validar_proprietario(notificacao, usuario.id)
    notificacao_service.deletar_notificacao(db, notificacao)
    return Mensagem(mensagem="Notificação excluída com sucesso")
