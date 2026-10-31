from typing import Optional

from pydantic import BaseModel


class ResultadoBusca(BaseModel):
    tipo: str
    id: int
    titulo: str
    descricao: Optional[str] = None
    extra: Optional[str] = None


class RespostaBusca(BaseModel):
    termo: str
    total: int
    resultados: list[ResultadoBusca]
