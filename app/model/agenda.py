from sqlalchemy import Column, Integer, String, DateTime, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base

class MensalidadeCliente(Base):
    __tablename__ = "mensalidades_clientes"

    id = Column(Integer, primary_key=True, index=True)
    nome_cliente = Column(String(150), nullable=False)
    valor = Column(Numeric(10, 2), nullable=False)
    date_vencimento = Column(DateTime(timezone=True), nullable=False)
    status_pagamento = Column(String(50), default="PENDENTE")
    observacao = Column(String(255), nullable=True)

class TarefaPessoal(Base):
    __tablename__ = "tarefas_pessoais"

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String(150), nullable=False)
    descricao = Column(String(500), nullable=True)
    data_limite = Column(DateTime(timezone=True), nullable=True)
    status = Column(String(50), default="PENDENTE")

    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    usuario = relationship("Usuario", back_populates="tarefas_pessoais")

class Reuniao(Base):
    __tablename__ = "reunioes"

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String(150), nullable=False)
    descricao = Column(String(500), nullable=True)
    data_hora_inicio = Column(DateTime(timezone=True), nullable=False)
    data_hora_fim = Column(DateTime(timezone=True), nullable=False)
    link_reuniao = Column(String(255), nullable=True)

    criador_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    criador = relationship("Usuario", back_populates="reunioes_criadas")

    from app.model.usuario import participantes_reuniao
    participantes = relationship("Usuario", secondary=participantes_reuniao, back_populates="reunioes_participando")