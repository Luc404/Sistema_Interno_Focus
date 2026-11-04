"""Modelos de agenda e finanças.

Define as mensalidades de clientes, as tarefas pessoais dos usuários e as
reuniões, incluindo o relacionamento de participantes.
"""

from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import relationship

from app.database import Base
from app.model.usuario import participantes_reuniao


class MensalidadeCliente(Base):
    """Representa a mensalidade de um cliente e o seu status de pagamento."""

    __tablename__ = "mensalidades_clientes"

    id = Column(Integer, primary_key=True, index=True)
    nome_cliente = Column(String(150), nullable=False)
    valor = Column(Numeric(10, 2), nullable=False)
    # Data em que a mensalidade vence e, quando paga, a data do pagamento.
    data_vencimento = Column(DateTime(timezone=True), nullable=False)
    data_pagamento = Column(DateTime(timezone=True), nullable=True)
    status_pagamento = Column(String(50), default="PENDENTE", nullable=False)
    observacao = Column(String(255), nullable=True)


class TarefaPessoal(Base):
    """Tarefa de uso individual, vinculada ao usuário que a criou."""

    __tablename__ = "tarefas_pessoais"

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String(150), nullable=False)
    descricao = Column(String(500), nullable=True)
    data_limite = Column(DateTime(timezone=True), nullable=True)
    status = Column(String(50), default="PENDENTE", nullable=False)

    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    usuario = relationship("Usuario", back_populates="tarefas_pessoais")


class Reuniao(Base):
    """Reunião com período definido, criador e lista de participantes."""

    __tablename__ = "reunioes"

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String(150), nullable=False)
    descricao = Column(String(500), nullable=True)
    data_hora_inicio = Column(DateTime(timezone=True), nullable=False)
    data_hora_fim = Column(DateTime(timezone=True), nullable=False)
    link_reuniao = Column(String(255), nullable=True)

    criador_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    criador = relationship("Usuario", back_populates="reunioes_criadas")
    # Relacionamento muitos-para-muitos com usuários via tabela associativa.
    participantes = relationship(
        "Usuario",
        secondary=participantes_reuniao,
        back_populates="reunioes_participando",
    )
