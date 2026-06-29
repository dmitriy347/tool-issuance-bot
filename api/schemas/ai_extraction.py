from pydantic import BaseModel


class ExtractedNames(BaseModel):
    """Схема для валидации данных, извлеченных из скриншота через AI."""
    primary: str
    second: str | None = None
    third: str | None = None