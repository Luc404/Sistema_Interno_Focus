from datetime import datetime

from pydantic import BaseModel


class ReuniaoResumo(BaseModel):
    id: int
    titulo: str
    data_hora_inicio: datetime

    class Config:
        from_attributes = True


class DashboardResumo(BaseModel):
    usuarios_ativos: int
    setores_ativos: int
    arquivos: int
    itens_backlog: int
    itens_backlog_pendentes: int
    mensalidades_pendentes: int
    mensalidades_valor_pendente: float
    tarefas_pendentes: int
    reunioes_hoje: int
    chatbots_ativos: int
    notebooks: int
    notificacoes_nao_lidas: int
    proximas_reunioes: list[ReuniaoResumo]
