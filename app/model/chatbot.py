"""Modelos de chatbots e mensagens.

Representa os chatbots configurados, seu criador e o histórico de
mensagens trocadas em cada conversa.
"""

from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database import Base


class Chatbot(Base):
    """Configuração de um chatbot, incluindo versão, status e modelo utilizado."""

    __tablename__ = "chatbots"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(120), nullable=False)
    descricao = Column(String(255), nullable=True)
    versao = Column(String(30), default="v1.0", nullable=False)
    status = Column(String(30), default="OFFLINE", nullable=False)
    modelo = Column(String(80), default="gpt-4o", nullable=False)
    data_criacao = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    criador_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)

    criador = relationship("Usuario", back_populates="chatbots_criados")
    # Ao excluir o chatbot, suas mensagens também são removidas.
    mensagens = relationship("ChatMensagem", back_populates="chatbot", cascade="all, delete-orphan")


class ChatMensagem(Base):
    """Mensagem de uma conversa, indicando o papel do autor e o conteúdo."""

    __tablename__ = "chat_mensagens"

    id = Column(Integer, primary_key=True, index=True)
    chatbot_id = Column(Integer, ForeignKey("chatbots.id", ondelete="CASCADE"), nullable=False)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    # Papel da mensagem na conversa, como USER ou ASSISTANT.
    papel = Column(String(20), nullable=False)
    conteudo = Column(Text, nullable=False)
    criado_em = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    chatbot = relationship("Chatbot", back_populates="mensagens")
    usuario = relationship("Usuario", back_populates="mensagens_chat")
