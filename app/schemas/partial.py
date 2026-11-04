"""Base compartilhada para os schemas de atualização parcial (PATCH).

Este módulo define a classe :class:`PartialUpdate`, usada como classe-mãe
por todos os schemas ``*Update`` do sistema. Ela centraliza duas regras
comuns a qualquer edição parcial:

1. Strings vazias (ou apenas com espaços) são convertidas em ``None``,
   permitindo que o cliente "limpe" um campo opcional enviando ``""``.
2. Ao menos um campo precisa ser informado na requisição; caso contrário
   a validação falha com erro, evitando atualizações vazias.
"""

from typing import ClassVar

from pydantic import BaseModel, field_validator, model_validator


class PartialUpdate(BaseModel):
    """Classe-base para atualizações parciais de recursos.

    O objetivo é permitir que os schemas de ``Update`` tenham todos os
    campos opcionais (com ``default=None``) sem que isso torne possível
    enviar um corpo vazio. As subclasses herdam automaticamente:

    - a conversão de string vazia em ``None``;
    - a exigência de ao menos um campo preenchido.

    Por que todos os campos viram opcionais? Em uma atualização parcial
    (PATCH) o cliente envia somente o que deseja alterar. Se os campos
    continuassem obrigatórios, seria necessário reenviar todo o recurso.
    Tornando-os ``Optional`` com valor padrão ``None``, o Pydantic passa a
    distinguir "campo não enviado" de "campo enviado com valor", e a lógica
    de persistência pode aplicar apenas os campos realmente presentes.
    """

    # Conjunto de nomes de campos que podem ser explicitamente "limpos"
    # (definidos como ``None``) sem que isso conte como ausência de dados.
    # É uma ClassVar porque pertence à classe, não a cada instância, e não
    # deve fazer parte do schema de entrada/saída. Subclasses podem
    # sobrescrevê-la, por exemplo: ``campos_limpaveis = frozenset({"descricao"})``.
    campos_limpaveis: ClassVar[frozenset[str]] = frozenset()

    @field_validator("*", mode="before")
    @classmethod
    def vazio_para_none(cls, value):
        """Converte strings vazias ou só com espaços em ``None``.

        O validador roda no modo ``before`` (antes da coerção de tipos de
        cada campo) e para todos os campos (``"*"``). Assim, enviar
        ``""`` equivale a enviar ``null``, o que facilita limpar campos
        opcionais em uma atualização parcial.
        """
        # Se o valor recebido é texto e, removendo os espaços, fica vazio,
        # tratamos como "sem valor".
        if isinstance(value, str) and value.strip() == "":
            return None
        return value

    @model_validator(mode="after")
    def ao_menos_um_campo(self):
        """Garante que ao menos um campo foi enviado para atualização.

        Roda após a validação dos campos. Considera válido o payload que:

        - tenha algum campo com valor diferente de ``None`` (ignorando os
          campos listados em ``campos_limpaveis``); ou
        - tenha enviado explicitamente um campo "limpável" (mesmo que o
          valor final seja ``None``), usando ``model_fields_set`` para
          saber o que veio na requisição.
        """
        # ``model_dump()`` gera um dicionário com os valores já validados.
        valores = self.model_dump()

        # Primeiro caso: existe algum campo "normal" com valor preenchido.
        # Campos em ``campos_limpaveis`` são ignorados aqui porque o valor
        # ``None`` neles é intencional e não deve contar como preenchimento.
        if any(
            valor is not None
            for campo, valor in valores.items()
            if campo not in self.campos_limpaveis
        ):
            return self

        # Segundo caso: o cliente enviou ao menos um campo "limpável".
        # ``model_fields_set`` contém os nomes dos campos recebidos, então a
        # interseção indica se algum deles foi informado (mesmo como None).
        if self.campos_limpaveis & self.model_fields_set:
            return self

        # Nenhum campo útil foi enviado: rejeita o payload vazio.
        raise ValueError("Envie ao menos um campo para editar")
