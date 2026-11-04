"""Serviço do dashboard.

Agrega indicadores gerais do sistema (usuários, setores, arquivos, backlog,
financeiro, tarefas, reuniões, chatbots, notebooks e notificações) em um único
resumo, além das próximas reuniões agendadas.
"""

from datetime import datetime, time, timezone
from decimal import Decimal

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.model.agenda import MensalidadeCliente, Reuniao, TarefaPessoal
from app.model.backlog import ItemBacklog
from app.model.biblioteca import Arquivo
from app.model.chatbot import Chatbot
from app.model.notebook import Notebook
from app.model.notificacao import Notificacao
from app.model.setor import Setor
from app.model.usuario import Usuario
from app.schemas.dashboard_schema import DashboardResumo, ReuniaoResumo


def resumo(db: Session, usuario: Usuario) -> DashboardResumo:
    """Calcula o resumo consolidado exibido no dashboard.

    Vários indicadores são globais, mas alguns são específicos do usuário
    autenticado (tarefas pendentes e notificações não lidas).

    Args:
        db: Sessão do SQLAlchemy.
        usuario: Usuário autenticado que está consultando o dashboard.

    Returns:
        Um ``DashboardResumo`` com as contagens, valores financeiros e as
        próximas reuniões.

    Raises:
        Nenhuma exceção de negócio; erros de banco são propagados.
    """
    # Data/hora atual em UTC para comparações consistentes com o banco.
    agora = datetime.now(timezone.utc)
    # Limites do dia atual (00:00:00 até 23:59:59.999999) em UTC.
    inicio_dia = datetime.combine(agora.date(), time.min, tzinfo=timezone.utc)
    fim_dia = datetime.combine(agora.date(), time.max, tzinfo=timezone.utc)

    # Soma dos valores ainda não recebidos (pendentes + atrasados).
    # coalesce evita NULL quando não há linhas; o ``or Decimal("0")`` cobre
    # o caso de scalar() retornar None.
    valor_pendente = (
        db.query(func.coalesce(func.sum(MensalidadeCliente.valor), 0))
        .filter(MensalidadeCliente.status_pagamento.in_(["PENDENTE", "ATRASADO"]))
        .scalar()
        or Decimal("0")
    )

    # As 5 próximas reuniões a partir de agora, em ordem cronológica.
    proximas = (
        db.query(Reuniao)
        .filter(Reuniao.data_hora_inicio >= agora)
        .order_by(Reuniao.data_hora_inicio)
        .limit(5)
        .all()
    )

    return DashboardResumo(
        # func.count conta linhas; filtros opcionais restringem o universo.
        usuarios_ativos=db.query(func.count(Usuario.id)).filter(Usuario.ativo.is_(True)).scalar() or 0,
        setores_ativos=db.query(func.count(Setor.id)).filter(Setor.status == "ATIVO").scalar() or 0,
        # Contagens globais sem filtro.
        arquivos=db.query(func.count(Arquivo.id)).scalar() or 0,
        itens_backlog=db.query(func.count(ItemBacklog.id)).scalar() or 0,
        # Itens ainda não concluídos.
        itens_backlog_pendentes=(
            db.query(func.count(ItemBacklog.id))
            .filter(ItemBacklog.status != "CONCLUIDO")
            .scalar()
            or 0
        ),
        # Mensalidades em aberto (pendentes ou atrasadas).
        mensalidades_pendentes=(
            db.query(func.count(MensalidadeCliente.id))
            .filter(MensalidadeCliente.status_pagamento.in_(["PENDENTE", "ATRASADO"]))
            .scalar()
            or 0
        ),
        # Converte Decimal para float para serialização no schema.
        mensalidades_valor_pendente=float(valor_pendente),
        # Tarefas pendentes apenas do usuário autenticado.
        tarefas_pendentes=(
            db.query(func.count(TarefaPessoal.id))
            .filter(
                TarefaPessoal.usuario_id == usuario.id,
                TarefaPessoal.status != "CONCLUIDA",
            )
            .scalar()
            or 0
        ),
        # Reuniões cujo início cai dentro do dia atual.
        reunioes_hoje=(
            db.query(func.count(Reuniao.id))
            .filter(
                Reuniao.data_hora_inicio >= inicio_dia,
                Reuniao.data_hora_inicio <= fim_dia,
            )
            .scalar()
            or 0
        ),
        # Chatbots considerados ativos (dois possíveis valores de status).
        chatbots_ativos=(
            db.query(func.count(Chatbot.id))
            .filter(Chatbot.status.in_(["ACTIVE", "ONLINE"]))
            .scalar()
            or 0
        ),
        notebooks=db.query(func.count(Notebook.id)).scalar() or 0,
        # Notificações não lidas apenas do usuário autenticado.
        notificacoes_nao_lidas=(
            db.query(func.count(Notificacao.id))
            .filter(
                Notificacao.usuario_id == usuario.id,
                Notificacao.lida.is_(False),
            )
            .scalar()
            or 0
        ),
        # Converte cada reunião ORM no schema resumido usando model_validate.
        proximas_reunioes=[ReuniaoResumo.model_validate(r) for r in proximas],
    )
