from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import timezone, datetime
from app.database import Base

class Arquivo(Base):
    __tablename__ = "arquivos"

    id = Column(Integer, primary_key = True, index = True)
    titulo = Column(String(100), nullable = False, index = True)
    caminho_arquivo = Column(String(200), nullable = False, unique = True)
    tipo_mime = Column(String(100), nullable = False)
    categoria = Column(String(100), nullable = False, index = True)
    tamanho_bytes = Column(Integer, nullable = False)
    data_upload = Column(DateTime(timezone = True), default = lambda: datetime.now(timezone.utc))

    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable = False)
    usuario = relationship("Usuario", back_populates = "arquivos")

class Link(Base):
    __tablename__ = "links"

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String(160),nullable= False)
    url = Column(String(500), nullable=False)
    descricao = Column(String(255), nullable=True)
    data_criacao = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable = False)
    usuario = relationship("Usuario", back_populates = "links")