"""Configuração de acesso ao banco de dados da aplicação.

Este módulo centraliza a criação do engine SQLAlchemy, da fábrica de sessões
(``SessionLocal``) e da classe base declarativa (``Base``) usada por todos os
modelos ORM. Também expõe a dependência ``get_db`` para injeção nas rotas do
FastAPI e a função ``init_db`` para criar as tabelas na inicialização.
"""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from app.core.config import get_settings

# Carrega as configurações da aplicação (inclui a URL do banco de dados).
settings = get_settings()

# O SQLite por padrão exige que a conexão seja usada na mesma thread em que foi
# criada. Como o FastAPI pode atender requisições em threads diferentes,
# desabilitamos essa checagem somente quando o banco é SQLite. Para outros
# bancos (ex.: PostgreSQL) não é necessário passar argumentos extras.
connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}

# Engine principal da aplicação. ``pool_pre_ping`` testa a conexão antes de usá-la,
# descartando conexões que tenham caído (evita erros de conexão "stale").
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    connect_args=connect_args,
)

# Fábrica de sessões. ``autocommit`` e ``autoflush`` desabilitados dão controle
# explícito das transações; todas as sessões são vinculadas ao ``engine`` acima.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# Classe base declarativa: todos os modelos ORM herdam dela para que o
# SQLAlchemy registre suas tabelas em ``Base.metadata``.
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """Fornece uma sessão de banco de dados por requisição (dependência FastAPI).

    Abre uma nova sessão a partir de ``SessionLocal``, entrega ao consumidor via
    ``yield`` e garante o fechamento da sessão ao final, mesmo em caso de erro.

    Yields:
        Session: sessão SQLAlchemy ativa para uso na requisição.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        # Fecha a sessão e devolve a conexão ao pool, independente de sucesso/erro.
        db.close()


def init_db() -> None:
    """Cria todas as tabelas registradas no metadata do SQLAlchemy.

    A importação de ``app.model`` é necessária para que todos os módulos de
    modelos sejam carregados e registrem suas tabelas em ``Base.metadata`` antes
    da criação. ``create_all`` é idempotente: só cria tabelas que ainda não
    existem.
    """
    import app.model  # noqa: F401  (registra todos os modelos no metadata)

    Base.metadata.create_all(bind=engine)
