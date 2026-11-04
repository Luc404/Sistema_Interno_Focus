"""Pacote de modelos ORM da aplicação.

Importa todos os modelos SQLAlchemy para que sejam registrados no metadata da
``Base`` e fiquem disponíveis por meio de um único ponto de importação. Expõe
também a lista ``__all__`` com os nomes públicos do pacote.
"""

# Importações dos modelos de cada domínio da aplicação. Manter esses imports
# aqui garante que o SQLAlchemy conheça todas as tabelas e relacionamentos.
from app.model.agenda import MensalidadeCliente, Reuniao, TarefaPessoal
from app.model.backlog import ItemBacklog
from app.model.biblioteca import Arquivo, Link
from app.model.categoria import Categoria, Pasta
from app.model.chatbot import ChatMensagem, Chatbot
from app.model.notebook import Notebook
from app.model.notificacao import Notificacao
from app.model.setor import Setor
from app.model.usuario import Usuario, participantes_reuniao

# Nomes exportados publicamente ao importar ``app.model``.
__all__ = [
    "MensalidadeCliente",
    "Reuniao",
    "TarefaPessoal",
    "ItemBacklog",
    "Arquivo",
    "Link",
    "Categoria",
    "Pasta",
    "ChatMensagem",
    "Chatbot",
    "Notebook",
    "Notificacao",
    "Setor",
    "Usuario",
    "participantes_reuniao",
]
