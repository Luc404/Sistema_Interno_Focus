"""Configuracao de execucao do Alembic para o projeto.

Responsavel por conectar o Alembic as configuracoes da aplicacao (URL do banco),
carregar os metadados dos modelos para o autogenerate e executar as migracoes
tanto em modo "offline" (gera SQL sem conectar) quanto "online" (executa
diretamente no banco).
"""

from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

from app.core.config import get_settings
from app.database import Base
import app.model  # noqa: F401  (registra todos os modelos)

# Objeto de configuracao do Alembic (equivalente ao alembic.ini).
config = context.config
settings = get_settings()
# Sobrescreve a URL do banco definida no alembic.ini pela configuracao da app,
# garantindo que as migracoes usem o mesmo banco da aplicacao.
config.set_main_option("sqlalchemy.url", settings.database_url)

# Configura o logging a partir do arquivo .ini, quando disponivel.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Metadados alvo do autogenerate: refletem todas as tabelas dos modelos.
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Executa as migracoes em modo offline (sem conexao real).

    Gera o SQL das migracoes usando apenas a URL e os metadados. ``literal_binds``
    embute os valores diretamente no SQL, e ``compare_type`` faz o autogenerate
    detectar mudancas de tipo de coluna.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Executa as migracoes conectando ao banco de dados real.

    Cria um engine a partir da secao de configuracao do Alembic. ``NullPool``
    evita reutilizacao de conexoes, o que e recomendado para migracoes.
    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )

        # Toda a migracao roda dentro de uma unica transacao.
        with context.begin_transaction():
            context.run_migrations()


# Escolhe o modo de execucao conforme a flag passada ao Alembic.
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
