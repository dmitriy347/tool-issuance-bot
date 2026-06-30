import re

from pydantic import BaseModel, field_validator


CYRILLIC_PATTERN = re.compile(r"^[А-Яа-яЁё\-]+$")

class ExtractedNames(BaseModel):
    """Схема для валидации данных, извлеченных из скриншота через AI."""
    primary: str
    second: str | None = None
    third: str | None = None

    @field_validator("primary", "second", "third")
    @classmethod
    def validate_cyrillic(cls, value: str | None) -> str | None:
        """Валидация, что все фамилии написаны кириллицей."""
        if value is not None and not CYRILLIC_PATTERN.fullmatch(value):
            raise ValueError(f"Фамилия должна быть написана кириллицей: {value!r}")
        return value