"""Modelo ORM de usuários e tabela associativa de participantes de reuniões.

Define a entidade ``Usuario``, com dados de autenticação, perfil e vínculos com
setor, e a tabela ``participantes_reuniao`` que implementa o relacionamento
muitos-para-muitos entre usuários e reuniões.
"""

from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Table
from sqlalchemy.orm import relationship

from app.database import Base

# Tabela associativa do relacionamento muitos-para-muitos entre reuniões e
# usuários. Como não há atributos próprios além das chaves, usa-se ``Table`` em
# vez de uma classe de modelo. As duas colunas formam a chave primária composta
# e ``ondelete="CASCADE"`` remove os vínculos quando a reunião ou o usuário é
# excluído.
participantes_reuniao = Table(
    "participantes_reuniao",
    Base.metadata,
    Column("reuniao_id", Integer, ForeignKey("reunioes.id", ondelete="CASCADE"), primary_key=True),
    Column("usuario_id", Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), primary_key=True),
)


class Usuario(Base):
    """Representa um usuário do sistema.

    Armazena dados cadastrais e de autenticação (nome, e-mail, hash de senha),
    o perfil de acesso, o status ativo e o setor ao qual pertence. Também expõe
    os relacionamentos com os demais recursos criados ou associados ao usuário
    (arquivos, links, tarefas, backlog, reuniões, notificações, chats e notas).
    """

    __tablename__ = "usuarios"

    # Chave primária do usuário.
    id = Column(Integer, primary_key=True, index=True)
    # Nome completo do usuário.
    nome_completo = Column(String(150), nullable=False)
    # E-mail usado como identificador de login; único e indexado.
    email = Column(String(150), nullable=False, unique=True, index=True)
    # Hash da senha (nunca a senha em texto puro).
    senha_hash = Column(String(255), nullable=False)
    # Cargo/função do usuário; campo opcional.
    cargo = Column(String(100), nullable=True)
    # Perfil de acesso do usuário (ex.: "MEMBRO"); valor padrão "MEMBRO".
    perfil = Column(String(255), default="MEMBRO", nullable=False)
    # Indica se o usuário está ativo no sistema; inicia como True.
    ativo = Column(Boolean, default=True, nullable=False)
    # Data de cadastro preenchida automaticamente em UTC.
    data_cadastro = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Chave estrangeira para o setor do usuário; opcional (usuário pode não ter setor).
    setor_id = Column(Integer, ForeignKey("setores.id"), nullable=True)

    # Setor ao qual o usuário pertence; contraparte de ``Setor.usuarios``.
    setor = relationship("Setor", back_populates="usuarios")
    # Arquivos enviados pelo usuário.
    arquivos = relationship("Arquivo", back_populates="usuario")
    # Links cadastrados pelo usuário.
    links = relationship("Link", back_populates="usuario")
    # Tarefas pessoais do usuário.
    tarefas_pessoais = relationship("TarefaPessoal", back_populates="usuario")
    # Itens de backlog de autoria do usuário; ``back_populates`` aponta para
    # ``ItemBacklog.autor``.
    items_backlog = relationship("ItemBacklog", back_populates="autor")
    # Reuniões criadas pelo usuário (papel de criador).
    reunioes_criadas = relationship("Reuniao", back_populates="criador")
    # Reuniões das quais o usuário participa. Relacionamento muitos-para-muitos
    # mediado pela tabela associativa ``participantes_reuniao``.
    reunioes_participando = relationship(
        "Reuniao",
        secondary=participantes_reuniao,
        back_populates="participantes",
    )
    # Notificações destinadas ao usuário.
    notificacoes = relationship("Notificacao", back_populates="usuario")
    # Chatbots criados pelo usuário.
    chatbots_criados = relationship("Chatbot", back_populates="criador")
    # Mensagens enviadas pelo usuário nos chats.
    mensagens_chat = relationship("ChatMensagem", back_populates="usuario")
    # Anotações (notebooks) de autoria do usuário.
    notebooks = relationship("Notebook", back_populates="autor")
