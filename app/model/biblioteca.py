"""Modelos da biblioteca de arquivos e links.

Armazena os metadados dos arquivos enviados, sua organização por categoria
e pasta, além dos links úteis cadastrados pelos usuários.
"""

from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class Arquivo(Base):
    """Metadados de um arquivo enviado e seus vínculos de organização."""

    __tablename__ = "arquivos"

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String(100), nullable=False, index=True)
    # Caminho único do arquivo no armazenamento.
    caminho_arquivo = Column(String(500), nullable=False, unique=True)
    tipo_mime = Column(String(100), nullable=False)
    categoria = Column(String(100), nullable=True, index=True)
    tamanho_bytes = Column(Integer, nullable=False)
    data_upload = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    categoria_id = Column(Integer, ForeignKey("categorias.id"), nullable=True)
    pasta_id = Column(Integer, ForeignKey("pastas.id"), nullable=True)

    usuario = relationship("Usuario", back_populates="arquivos")
    categoria_rel = relationship("Categoria", back_populates="arquivos")
    pasta = relationship("Pasta", back_populates="arquivos")


class Link(Base):
    """Link útil cadastrado por um usuário, com categoria opcional."""

    __tablename__ = "links"

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String(160), nullable=False)
    url = Column(String(500), nullable=False)
    descricao = Column(String(255), nullable=True)
    categoria = Column(String(100), nullable=True, index=True)
    data_criacao = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    usuario = relationship("Usuario", back_populates="links")
