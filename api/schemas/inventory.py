from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class InventoryBase(BaseModel):
    """Общие поля для инвентаря. Основа для других схем."""
    employee_name: str
    tool_name: str
    tool_code: str
    quantity: int
    price: Decimal
    period: date


class InventoryCreate(InventoryBase):
    """Схема для создания нового инвентаря. Все поля обязательны."""
    pass


class InventoryResponse(InventoryBase):
    """Схема ответа API для инвентаря. Содержит все поля, возвращаемые клиенту."""
    id: int

    model_config = ConfigDict(from_attributes=True)
