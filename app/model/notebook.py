"""Modelo ORM de anotações pessoais (notebooks).

Representa as notas/cadernos criados pelos usuários, contendo agrupamento,
título, conteúdo livre e tags, além do vínculo com o autor.
"""

from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database import Base


class Notebook(Base):
    """Representa uma anotação (notebook) pertencente a um usuário.

    Cada notebook pertence a exatamente um usuário (autor), possui um grupo
    para organização, um título, conteúdo em texto livre e tags opcionais.
    """

    __tablename__ = "notebooks"

    # Chave primária da anotação.
    id = Column(Integer, primary_key=True, index=True)
    # Agrupamento/categoria da nota; valor padrão "PERSONAL NOTES".
    grupo = Column(String(80), default="PERSONAL NOTES", nullable=False, index=True)
    # Título da anotação; indexado para facilitar buscas por nome.
    titulo = Column(String(150), nullable=False, index=True)
    # Subtítulo opcional da anotação.
    subtitulo = Column(String(255), nullable=True)
    # Conteúdo completo da nota (texto longo, sem limite fixo de tamanho).
    conteudo = Column(Text, nullable=False)
    # Tags livres para classificação; campo opcional.
    tags = Column(String(255), nullable=True)
    # Data de criação preenchida automaticamente em UTC.
    data_criacao = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    # Data da última atualização, recalculada automaticamente a cada update.
    data_atualizacao = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Chave estrangeira para o usuário autor da anotação (obrigatória).
    autor_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    # Relacionamento com o autor; ``back_populates`` liga ao atributo
    # ``Usuario.notebooks``, mantendo a navegação nos dois sentidos.
    autor = relationship("Usuario", back_populates="notebooks")
