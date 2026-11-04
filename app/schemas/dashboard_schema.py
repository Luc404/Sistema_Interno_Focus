"""Schemas Pydantic do painel (dashboard) do sistema.

Define o resumo condensado de uma reunião e o agregado de indicadores
exibido no dashboard, reunindo contadores de várias entidades.
"""

from datetime import datetime

from pydantic import BaseModel


class ReuniaoResumo(BaseModel):
    """Versão resumida de uma reunião para exibição no dashboard."""

    id: int
    titulo: str
    # Data/hora de início da reunião.
    data_hora_inicio: datetime

    class Config:
        # Permite construir o schema a partir de objetos ORM.
        from_attributes = True


class DashboardResumo(BaseModel):
    """Agregado de indicadores exibidos no painel principal."""

    # Quantidade de usuários ativos.
    usuarios_ativos: int
    # Quantidade de setores ativos.
    setores_ativos: int
    # Total de arquivos cadastrados.
    arquivos: int
    # Total de itens no backlog.
    itens_backlog: int
    # Itens de backlog ainda pendentes.
    itens_backlog_pendentes: int
    # Mensalidades com pagamento pendente.
    mensalidades_pendentes: int
    # Soma dos valores ainda pendentes de recebimento.
    mensalidades_valor_pendente: float
    # Tarefas pessoais pendentes.
    tarefas_pendentes: int
    # Reuniões agendadas para hoje.
    reunioes_hoje: int
    # Chatbots atualmente ativos.
    chatbots_ativos: int
    # Total de notebooks cadastrados.
    notebooks: int
    # Notificações ainda não lidas.
    notificacoes_nao_lidas: int
    # Lista das próximas reuniões (versão resumida).
    proximas_reunioes: list[ReuniaoResumo]
