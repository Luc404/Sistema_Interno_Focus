from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class Categoria(Base):
    __tablename__ = "categorias"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False, unique=True, index=True)
    descricao = Column(String(255), nullable=True)
    data_criacao = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    arquivos = relationship("Arquivo", back_populates="categoria_rel")


class Pasta(Base):
    __tablename__ = "pastas"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False, index=True)
    descricao = Column(String(255), nullable=True)
    pasta_pai_id = Column(Integer, ForeignKey("pastas.id"), nullable=True)
    data_criacao = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    pasta_pai = relationship("Pasta", remote_side=[id], back_populates="subpastas")
    subpastas = relationship("Pasta", back_populates="pasta_pai")
    arquivos = relationship("Arquivo", back_populates="pasta")
