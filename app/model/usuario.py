from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Table
from sqlalchemy.orm import relationship

from app.database import Base

participantes_reuniao = Table(
    "participantes_reuniao",
    Base.metadata,
    Column("reuniao_id", Integer, ForeignKey("reunioes.id", ondelete="CASCADE"), primary_key=True),
    Column("usuario_id", Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), primary_key=True),
)


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nome_completo = Column(String(150), nullable=False)
    email = Column(String(150), nullable=False, unique=True, index=True)
    senha_hash = Column(String(255), nullable=False)
    cargo = Column(String(100), nullable=True)
    perfil = Column(String(255), default="MEMBRO", nullable=False)
    ativo = Column(Boolean, default=True, nullable=False)
    data_cadastro = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    setor_id = Column(Integer, ForeignKey("setores.id"), nullable=True)

    setor = relationship("Setor", back_populates="usuarios")
    arquivos = relationship("Arquivo", back_populates="usuario")
    links = relationship("Link", back_populates="usuario")
    tarefas_pessoais = relationship("TarefaPessoal", back_populates="usuario")
    items_backlog = relationship("ItemBacklog", back_populates="autor")
    reunioes_criadas = relationship("Reuniao", back_populates="criador")
    reunioes_participando = relationship(
        "Reuniao",
        secondary=participantes_reuniao,
        back_populates="participantes",
    )
    notificacoes = relationship("Notificacao", back_populates="usuario")
    chatbots_criados = relationship("Chatbot", back_populates="criador")
    mensagens_chat = relationship("ChatMensagem", back_populates="usuario")
    notebooks = relationship("Notebook", back_populates="autor")
