"""Schemas Pydantic para resultados da busca global.

Modela um item individual encontrado na busca e o envelope de resposta
que agrega o termo pesquisado, o total de ocorrências e a lista de
resultados.
"""

from typing import Optional

from pydantic import BaseModel


class ResultadoBusca(BaseModel):
    """Representa um único resultado retornado pela busca.

    ``tipo`` identifica a entidade de origem (ex.: arquivo, backlog,
    reunião) e ``extra`` carrega informação complementar específica
    daquele tipo.
    """

    # Tipo/categoria do registro encontrado.
    tipo: str
    # Identificador do registro na entidade de origem.
    id: int
    # Título exibido no resultado.
    titulo: str
    # Descrição opcional do registro.
    descricao: Optional[str] = None
    # Informação adicional opcional (ex.: caminho, data formatada).
    extra: Optional[str] = None


class RespostaBusca(BaseModel):
    """Envelope de resposta da busca, com termo, total e resultados."""

    # Termo pesquisado pelo usuário.
    termo: str
    # Quantidade total de resultados encontrados.
    total: int
    # Lista de resultados individuais.
    resultados: list[ResultadoBusca]
