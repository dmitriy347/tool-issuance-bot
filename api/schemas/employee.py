from datetime import date

from pydantic import BaseModel, ConfigDict


class EmployeeBase(BaseModel):
    """Базовая схема для сотрудника. Содержит общие поля."""
    full_name: str
    position: str
    contract_number: str
    contract_date: date


class EmployeeCreate(EmployeeBase):
    """Схема для создания нового сотрудника. Все поля обязательны."""
    pass


class EmployeeResponse(EmployeeBase):
    """Схема ответа API для сотрудника. Содержит все поля, возвращаемые клиенту."""
    id: int

    model_config = ConfigDict(from_attributes=True)
