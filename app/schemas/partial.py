from typing import ClassVar

from pydantic import BaseModel, field_validator, model_validator


class PartialUpdate(BaseModel):
    campos_limpaveis: ClassVar[frozenset[str]] = frozenset()

    @field_validator("*", mode="before")
    @classmethod
    def vazio_para_none(cls, value):
        if isinstance(value, str) and value.strip() == "":
            return None
        return value

    @model_validator(mode="after")
    def ao_menos_um_campo(self):
        valores = self.model_dump()

        if any(
            valor is not None
            for campo, valor in valores.items()
            if campo not in self.campos_limpaveis
        ):
            return self

        if self.campos_limpaveis & self.model_fields_set:
            return self

        raise ValueError("Envie ao menos um campo para editar")
