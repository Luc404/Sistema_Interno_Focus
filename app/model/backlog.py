from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base

class ItemBacklog(Base):
    __tablename__ = "items_backlog"

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String(150), nullable=False)
    descricao = Column(String(500), nullable=False)
    tipo = Column(String(50), nullable=False)
    prioridade = Column(String(50), default="MEDIA")
    status = Column(String(50), default="PENDENTE")
    data_criacao = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    autor_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    setor_id = Column(Integer, ForeignKey("setores.id"), nullable=False)

    autor = relationship("Usuario", back_populates="items_backlog")
    setor = relationship("Setor", back_populates="items_backlog")