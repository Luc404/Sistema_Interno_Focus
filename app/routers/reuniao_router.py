"""Router de reuniões da agenda.

Gerencia reuniões e seus participantes: criação (com notificação dos
convidados), listagem com filtros, próximas reuniões, consulta, atualização,
exclusão e inclusão/remoção de participantes (com notificação).

Endpoints expostos (prefixo ``/api/reunioes``):
- ``POST /``                                  -> cria reunião;
- ``GET /``                                   -> listagem paginada;
- ``GET /proximas``                           -> próximas reuniões;
- ``GET /{reuniao_id}``                       -> consulta reunião;
- ``PATCH /{reuniao_id}``                     -> atualização parcial;
- ``DELETE /{reuniao_id}``                    -> exclusão;
- ``GET /{reuniao_id}/participantes``         -> lista participantes;
- ``POST /{reuniao_id}/participantes/{usuario_id}``   -> adiciona participante;
- ``DELETE /{reuniao_id}/participantes/{usuario_id}`` -> remove participante.
"""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.deps import ensure_owner_or_admin, get_current_user
from app.database import get_db
from app.model.usuario import Usuario
from app.schemas.common import Mensagem, Page
from app.schemas.reuniao_schema import ReuniaoCreate, ReuniaoResponse, ReuniaoUpdate
from app.schemas.usuario_schema import UsuarioResumo
from app.services import notificacao_service, reuniao_service, usuario_service

# Prefixo e tag OpenAPI das rotas de reuniões.
router = APIRouter(prefix="/api/reunioes", tags=["Agenda - Reuniões"])


@router.post("/", response_model=ReuniaoResponse, status_code=status.HTTP_201_CREATED)
def criar_reuniao(
    reuniao: ReuniaoCreate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    """Cria uma reunião e notifica os participantes convidados.

    O criador é sempre o usuário autenticado (``criador_id``). Se houver
    ``participantes_ids``, cada convidado recebe uma notificação com link para
    a reunião.

    Autenticação: obrigatória.
    Retorno: ``ReuniaoResponse`` criada (HTTP 201).
    """
    db_reuniao = reuniao_service.criar_reuniao(db=db, reuniao=reuniao, criador_id=usuario.id)
    # Notificação em lote somente quando há participantes informados.
    if reuniao.participantes_ids:
        notificacao_service.criar_para_usuarios(
            db,
            reuniao.participantes_ids,
            titulo="Nova reunião agendada",
            mensagem=f"Você foi convidado para a reunião: {reuniao.titulo}",
            tipo="REUNIAO",
            link=f"/agenda/reunioes/{db_reuniao.id}",
        )
    return db_reuniao


@router.get("/", response_model=Page[ReuniaoResponse])
def listar_reunioes(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    busca: str | None = None,
    data_inicio: datetime | None = None,
    data_fim: datetime | None = None,
    criador_id: int | None = None,
    participante_id: int | None = None,
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    """Lista reuniões com paginação e filtros.

    ``skip``/``limit`` controlam a paginação (máximo de 500 por página).
    Filtros disponíveis: busca textual, intervalo de datas, criador e
    participante.

    Autenticação: obrigatória.
    Retorno: ``Page[ReuniaoResponse]``.
    """
    return reuniao_service.listar_reunioes(
        db=db,
        skip=skip,
        limit=limit,
        busca=busca,
        data_inicio=data_inicio,
        data_fim=data_fim,
        criador_id=criador_id,
        participante_id=participante_id,
    )


# Rota estática declarada antes de `/{reuniao_id}` para evitar conflito de match.
@router.get("/proximas", response_model=list[ReuniaoResponse])
def listar_proximas_reunioes(
    limite: int = Query(5, ge=1, le=50),
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    """Lista as próximas reuniões, ordenadas cronologicamente.

    Parâmetros:
    - ``limite``: quantidade máxima de reuniões (1 a 50; padrão 5).

    Autenticação: obrigatória.
    Retorno: lista de ``ReuniaoResponse``.
    """
    return reuniao_service.listar_proximas(db, limite)


@router.get("/{reuniao_id}", response_model=ReuniaoResponse)
def obter_reuniao(
    reuniao_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    """Consulta uma reunião pelo identificador.

    Autenticação: obrigatória.
    Retorno: ``ReuniaoResponse`` ou HTTP 404 se não existir.
    """
    db_reuniao = reuniao_service.obter_reuniao_por_id(db=db, reuniao_id=reuniao_id)
    if not db_reuniao:
        raise HTTPException(status_code=404, detail="Reunião não encontrada")
    return db_reuniao


@router.patch("/{reuniao_id}", response_model=ReuniaoResponse)
def atualizar_reuniao(
    reuniao_id: int,
    dados: ReuniaoUpdate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    """Atualiza parcialmente uma reunião.

    Apenas campos enviados são aplicados (``exclude_unset=True``).
    Autenticação/permissão: somente o criador da reunião ou ADMIN.
    Retorno: ``ReuniaoResponse`` atualizada; HTTP 404 se não existir.
    """
    db_reuniao = reuniao_service.obter_reuniao_por_id(db=db, reuniao_id=reuniao_id)
    if not db_reuniao:
        raise HTTPException(status_code=404, detail="Reunião não encontrada")
    # Garante que o usuário seja o criador da reunião ou administrador.
    ensure_owner_or_admin(usuario, db_reuniao.criador_id)
    return reuniao_service.atualizar_reuniao(
        db, db_reuniao, dados.model_dump(exclude_unset=True)
    )


@router.delete("/{reuniao_id}", response_model=Mensagem)
def deletar_reuniao(
    reuniao_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    """Exclui uma reunião.

    Autenticação/permissão: somente o criador da reunião ou ADMIN.
    Retorno: ``Mensagem`` de confirmação; HTTP 404 se não existir.
    """
    db_reuniao = reuniao_service.obter_reuniao_por_id(db=db, reuniao_id=reuniao_id)
    if not db_reuniao:
        raise HTTPException(status_code=404, detail="Reunião não encontrada")
    ensure_owner_or_admin(usuario, db_reuniao.criador_id)
    reuniao_service.deletar_reuniao(db, db_reuniao)
    return Mensagem(mensagem="Reunião excluída com sucesso")


@router.get("/{reuniao_id}/participantes", response_model=list[UsuarioResumo])
def listar_participantes(
    reuniao_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    """Lista os participantes de uma reunião.

    Autenticação: obrigatória.
    Retorno: lista de ``UsuarioResumo``; HTTP 404 se a reunião não existir.
    """
    db_reuniao = reuniao_service.obter_reuniao_por_id(db=db, reuniao_id=reuniao_id)
    if not db_reuniao:
        raise HTTPException(status_code=404, detail="Reunião não encontrada")
    return db_reuniao.participantes


@router.post("/{reuniao_id}/participantes/{usuario_id}", response_model=ReuniaoResponse)
def adicionar_participante(
    reuniao_id: int,
    usuario_id: int,
    db: Session = Depends(get_db),
    atual: Usuario = Depends(get_current_user),
):
    """Adiciona um participante à reunião e o notifica.

    Autenticação/permissão: somente o criador da reunião ou ADMIN.
    Retorno: ``ReuniaoResponse`` atualizada; HTTP 404 se a reunião ou o
    participante não existirem.
    """
    db_reuniao = reuniao_service.obter_reuniao_por_id(db=db, reuniao_id=reuniao_id)
    if not db_reuniao:
        raise HTTPException(status_code=404, detail="Reunião não encontrada")
    # Somente o criador ou um administrador pode alterar os participantes.
    ensure_owner_or_admin(atual, db_reuniao.criador_id)
    participante = usuario_service.obter_usuario_por_id(db, usuario_id)
    if not participante:
        raise HTTPException(status_code=404, detail="Participante não encontrado")
    db_reuniao = reuniao_service.adicionar_participante(db, db_reuniao, participante)
    # Notifica o novo participante sobre a inclusão na reunião.
    notificacao_service.criar_para_usuarios(
        db,
        [usuario_id],
        titulo="Convite para reunião",
        mensagem=f"Você foi adicionado à reunião: {db_reuniao.titulo}",
        tipo="REUNIAO",
        link=f"/agenda/reunioes/{db_reuniao.id}",
    )
    return db_reuniao


@router.delete("/{reuniao_id}/participantes/{usuario_id}", response_model=ReuniaoResponse)
def remover_participante(
    reuniao_id: int,
    usuario_id: int,
    db: Session = Depends(get_db),
    atual: Usuario = Depends(get_current_user),
):
    """Remove um participante da reunião.

    Autenticação/permissão: somente o criador da reunião ou ADMIN.
    Retorno: ``ReuniaoResponse`` atualizada; HTTP 404 se a reunião ou o
    participante não existirem.
    """
    db_reuniao = reuniao_service.obter_reuniao_por_id(db=db, reuniao_id=reuniao_id)
    if not db_reuniao:
        raise HTTPException(status_code=404, detail="Reunião não encontrada")
    ensure_owner_or_admin(atual, db_reuniao.criador_id)
    participante = usuario_service.obter_usuario_por_id(db, usuario_id)
    if not participante:
        raise HTTPException(status_code=404, detail="Participante não encontrado")
    return reuniao_service.remover_participante(db, db_reuniao, participante)
