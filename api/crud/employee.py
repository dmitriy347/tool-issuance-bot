from datetime import date

from sqlalchemy import select, delete

from sqlalchemy.ext.asyncio import AsyncSession

from models.employee import Employee


async def create(
        session: AsyncSession,
        full_name: str,
        position: str,
        contract_number: str,
        contract_date: date,
        document_type: str,
        id_series: str,
        id_number: str,
        id_issued_date: date,
        issued_by: str,
        address: str
) -> Employee:
    """Создаёт нового сотрудника в БД и возвращает его с заполненным id и данными."""
    employee = Employee(
        full_name = full_name,
        position = position,
        contract_number = contract_number,
        contract_date = contract_date,
        document_type = document_type,
        id_series = id_series,
        id_number = id_number,
        id_issued_date = id_issued_date,
        issued_by = issued_by,
        address = address
    )
    session.add(employee)
    await session.commit()
    await session.refresh(employee)
    return employee

async def get_by_name(session: AsyncSession, full_name: str) -> Employee | None:
    """Возвращает сотрудника по имени или None если не найден."""
    result = await session.execute(
        select(Employee).where(Employee.full_name == full_name)
    )
    # Вернуть 1 запись или None (если не найдена), если > 1 - упадет с ошибкой
    return result.scalar_one_or_none()

async def get_all(session: AsyncSession) -> list[Employee]:
    """Возвращает список всех сотрудников из БД."""
    result = await session.execute(select(Employee))
    return list(result.scalars().all())

async def delete_all(session: AsyncSession) -> None:
    """Удаление всех сотрудников."""
    await session.execute(delete(Employee))
    await session.commit()

async def get_by_name_fragment(session: AsyncSession, fragment: str) -> Employee | None:
    """Возвращает полное ФИО сотрудника по фрагменту имени или None если не найден."""
    result = await session.execute(
        select(Employee).where(Employee.full_name.ilike(f"{fragment}%"))
    )
    return result.scalar_one_or_none()