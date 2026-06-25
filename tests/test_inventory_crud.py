from sqlalchemy.ext.asyncio import AsyncSession

from api.crud.inventory import create, get_by_employee_name, delete_all

async def test_create_inventory(db_session: AsyncSession, inventory_data):
    """Тестирует создание инвентаря в БД и проверяет, что он был создан с правильными данными."""
    created_inventory = await create(db_session, **inventory_data)
    assert created_inventory is not None
    assert created_inventory.employee_name == inventory_data["employee_name"]


async def test_get_by_employee_name(db_session: AsyncSession, inventory_data):
    """Тестирует получение инвентаря по имени сотрудника."""
    await create(db_session, **inventory_data)
    inventories = await get_by_employee_name(db_session, inventory_data["employee_name"])
    assert len(inventories) > 0

async def test_delete_inventory(db_session: AsyncSession, inventory_data):
    """Тестирует удаление всего инвентаря из БД."""
    await create(db_session, **inventory_data)
    await delete_all(db_session)
    inventories = await get_by_employee_name(db_session, inventory_data["employee_name"])
    assert len(inventories) == 0
