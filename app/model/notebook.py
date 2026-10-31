from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database import Base


class Notebook(Base):
    __tablename__ = "notebooks"

    id = Column(Integer, primary_key=True, index=True)
    grupo = Column(String(80), default="PERSONAL NOTES", nullable=False, index=True)
    titulo = Column(String(150), nullable=False, index=True)
    subtitulo = Column(String(255), nullable=True)
    conteudo = Column(Text, nullable=False)
    tags = Column(String(255), nullable=True)
    data_criacao = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    data_atualizacao = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    autor_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    autor = relationship("Usuario", back_populates="notebooks")
