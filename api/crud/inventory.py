from datetime import date
from decimal import Decimal

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from models.inventory import Inventory


async def create(session:AsyncSession, employee_name: str, tool_name: str, tool_code: str, quantity: int, price: Decimal, period: date) -> Inventory:
    """Создает новый инвентарь в БД и возвращает его с заполненным id и данными."""
    inventory = Inventory(
        employee_name = employee_name,
        tool_name = tool_name,
        tool_code = tool_code,
        quantity = quantity,
        price = price,
        period = period,
    )
    session.add(inventory)  # Добавляем объект inventory в сессию, но он еще не сохранен в БД
    await session.commit()  # Сохраняем изменения в БД
    await session.refresh(inventory)  # Подгружаем id из БД, который был сгенерирован автоматически
    return inventory

async def get_by_employee_name(session: AsyncSession, employee_name: str) -> list[Inventory] | None:
    """Возвращает инвентарь по имени сотрудника или None если не найден."""
    result = await session.execute(
        select(Inventory).where(Inventory.employee_name == employee_name)
    )
    return result.scalars().all()  # Вернет список всех записей, соответствующих условию, или пустой список, если не найдено

async def delete_all(session: AsyncSession) -> None:
    """Удаление всего инвентаря."""
    await session.execute(delete(Inventory))
    await session.commit()
