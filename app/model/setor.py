"""Modelo ORM de setores da organização.

Um setor agrupa usuários e itens de backlog, funcionando como unidade
organizacional para filtros e permissões dentro do sistema.
"""

from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class Setor(Base):
    """Representa um setor/departamento ao qual usuários podem ser vinculados.

    Mantém o nome único do setor, uma descrição opcional, status e a data de
    criação, além dos relacionamentos com usuários e itens de backlog.
    """

    __tablename__ = "setores"

    # Chave primária do setor.
    id = Column(Integer, primary_key=True, index=True)
    # Nome do setor; único e indexado para evitar duplicidades e acelerar buscas.
    nome = Column(String(100), nullable=False, unique=True, index=True)
    # Descrição opcional do setor.
    descricao = Column(String(255), nullable=True)
    # Status do setor (ex.: "ATIVO"); valor padrão "ATIVO".
    status = Column(String(50), default="ATIVO", nullable=False)
    # Data de criação preenchida automaticamente em UTC.
    data_criacao = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Usuários pertencentes a este setor; contraparte de ``Usuario.setor``.
    usuarios = relationship("Usuario", back_populates="setor")
    # Itens de backlog associados a este setor; contraparte de
    # ``ItemBacklog.setor``.
    items_backlog = relationship("ItemBacklog", back_populates="setor")
