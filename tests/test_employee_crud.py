import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from api.crud.employee import create, get_by_name, get_all, delete_all, get_by_name_fragment, EmployeeError


async def test_create_employee(db_session: AsyncSession, employee_data):
    """Тестирует создание сотрудника в БД и проверяет, что он был создан с правильными данными."""
    # Создаём сотрудника в БД
    created_employee = await create(db_session, **employee_data)
    assert created_employee is not None


async def test_get_by_name(db_session: AsyncSession, employee_data):
    """Тестирует получение сотрудника по имени из БД."""
    # Создаём сотрудника в БД
    await create(db_session, **employee_data)
    # Получаем сотрудника по имени
    retrieved_employee = await get_by_name(db_session, employee_data["full_name"])
    assert retrieved_employee is not None
    assert retrieved_employee.full_name == employee_data["full_name"]


async def test_get_all_employees(db_session: AsyncSession, employee_data):
    """Тестирует получение всех сотрудников из БД."""
    # Создаём сотрудника в БД
    await create(db_session, **employee_data)
    # Получаем всех сотрудников
    employees = await get_all(db_session)
    assert len(employees) > 0


async def test_delete_all_employees(db_session: AsyncSession, employee_data):
    """Тестирует удаление всех сотрудников из БД."""
    # Создаём сотрудника в БД
    await create(db_session, **employee_data)
    # Удаляем всех сотрудников
    await delete_all(db_session)
    # Проверяем, что сотрудников больше нет
    employees = await get_all(db_session)
    assert len(employees) == 0


async def test_get_by_name_fragment(db_session: AsyncSession, employee_data):
    """Тестирует получение сотрудника по фрагменту имени из БД."""
    # Создаём сотрудника в БД
    await create(db_session, **employee_data)
    # Получаем сотрудника по фрагменту имени
    fragment = employee_data["full_name"].split()[0]  # Берём первую часть ФИО как фрагмент
    retrieved_employee = await get_by_name_fragment(db_session, fragment)
    assert retrieved_employee is not None
    assert retrieved_employee.full_name == employee_data["full_name"]


async def test_get_by_name_fragment_raises_on_ambiguous_match(db_session: AsyncSession, employee_data):
    """Если по фрагменту имени найдено больше одного сотрудника – поднимается исключение EmployeeError."""
    await create(db_session, **employee_data)
    second_employee_data = {**employee_data, "full_name": "Иванов Петр Петрович"}
    await create(db_session, **second_employee_data)

    fragment = employee_data["full_name"].split()[0]  # Берём первую часть ФИО как фрагмент – "Иванов"
    with pytest.raises(EmployeeError):
        await get_by_name_fragment(db_session, fragment)