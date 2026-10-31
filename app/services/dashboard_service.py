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
    agora = datetime.now(timezone.utc)
    inicio_dia = datetime.combine(agora.date(), time.min, tzinfo=timezone.utc)
    fim_dia = datetime.combine(agora.date(), time.max, tzinfo=timezone.utc)

    valor_pendente = (
        db.query(func.coalesce(func.sum(MensalidadeCliente.valor), 0))
        .filter(MensalidadeCliente.status_pagamento.in_(["PENDENTE", "ATRASADO"]))
        .scalar()
        or Decimal("0")
    )

    proximas = (
        db.query(Reuniao)
        .filter(Reuniao.data_hora_inicio >= agora)
        .order_by(Reuniao.data_hora_inicio)
        .limit(5)
        .all()
    )

    return DashboardResumo(
        usuarios_ativos=db.query(func.count(Usuario.id)).filter(Usuario.ativo.is_(True)).scalar() or 0,
        setores_ativos=db.query(func.count(Setor.id)).filter(Setor.status == "ATIVO").scalar() or 0,
        arquivos=db.query(func.count(Arquivo.id)).scalar() or 0,
        itens_backlog=db.query(func.count(ItemBacklog.id)).scalar() or 0,
        itens_backlog_pendentes=(
            db.query(func.count(ItemBacklog.id))
            .filter(ItemBacklog.status != "CONCLUIDO")
            .scalar()
            or 0
        ),
        mensalidades_pendentes=(
            db.query(func.count(MensalidadeCliente.id))
            .filter(MensalidadeCliente.status_pagamento.in_(["PENDENTE", "ATRASADO"]))
            .scalar()
            or 0
        ),
        mensalidades_valor_pendente=float(valor_pendente),
        tarefas_pendentes=(
            db.query(func.count(TarefaPessoal.id))
            .filter(
                TarefaPessoal.usuario_id == usuario.id,
                TarefaPessoal.status != "CONCLUIDA",
            )
            .scalar()
            or 0
        ),
        reunioes_hoje=(
            db.query(func.count(Reuniao.id))
            .filter(
                Reuniao.data_hora_inicio >= inicio_dia,
                Reuniao.data_hora_inicio <= fim_dia,
            )
            .scalar()
            or 0
        ),
        chatbots_ativos=(
            db.query(func.count(Chatbot.id))
            .filter(Chatbot.status.in_(["ACTIVE", "ONLINE"]))
            .scalar()
            or 0
        ),
        notebooks=db.query(func.count(Notebook.id)).scalar() or 0,
        notificacoes_nao_lidas=(
            db.query(func.count(Notificacao.id))
            .filter(
                Notificacao.usuario_id == usuario.id,
                Notificacao.lida.is_(False),
            )
            .scalar()
            or 0
        ),
        proximas_reunioes=[ReuniaoResumo.model_validate(r) for r in proximas],
    )
