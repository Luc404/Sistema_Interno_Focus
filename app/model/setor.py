from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class Setor(Base):
    __tablename__ = "setores"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False, unique=True, index=True)
    descricao = Column(String(255), nullable=True)
    status = Column(String(50), default="ATIVO", nullable=False)
    data_criacao = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    usuarios = relationship("Usuario", back_populates="setor")
    items_backlog = relationship("ItemBacklog", back_populates="setor")
