"""Modelo ORM de notificações destinadas aos usuários.

Cada notificação é entregue a um usuário específico e contém título,
mensagem, tipo, eventual link de ação e indicador de leitura.
"""

from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class Notificacao(Base):
    """Representa uma notificação individual enviada a um usuário.

    A notificação possui um tipo (ex.: "INFO"), um estado de leitura e pode
    apontar para um link relacionado ao evento que a originou.
    """

    __tablename__ = "notificacoes"

    # Chave primária da notificação.
    id = Column(Integer, primary_key=True, index=True)
    # Título curto exibido ao usuário.
    titulo = Column(String(150), nullable=False)
    # Corpo da mensagem da notificação.
    mensagem = Column(String(500), nullable=False)
    # Tipo/categoria da notificação; valor padrão "INFO".
    tipo = Column(String(30), default="INFO", nullable=False)
    # Link opcional para direcionar o usuário ao recurso relacionado.
    link = Column(String(255), nullable=True)
    # Indica se a notificação já foi lida pelo usuário; inicia como False.
    lida = Column(Boolean, default=False, nullable=False)
    # Data de criação preenchida automaticamente em UTC.
    data_criacao = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Chave estrangeira para o usuário destinatário. ``ondelete="CASCADE"`` faz
    # com que as notificações sejam removidas junto do usuário no banco.
    usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)
    # Relacionamento com o usuário; ``back_populates`` liga a ``Usuario.notificacoes``.
    usuario = relationship("Usuario", back_populates="notificacoes")
