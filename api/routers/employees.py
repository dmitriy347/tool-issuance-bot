from fastapi import APIRouter, Depends, HTTPException

from api.crud.employee import get_all, create, delete_all, get_by_name_fragment
from api.schemas.employee import EmployeeResponse, EmployeeCreate
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db

router = APIRouter(prefix="/employees", tags=["employees"])

@router.get("/", response_model=list[EmployeeResponse])
async def get_all_employees(db: AsyncSession = Depends(get_db)):
    """Возвращает список всех сотрудников."""
    return await get_all(db)

@router.post("/", response_model=EmployeeResponse)
async def create_employee(employee_data: EmployeeCreate, db: AsyncSession = Depends(get_db)):
    """Создает нового сотрудника"""
    return await create(db, **employee_data.model_dump())

@router.delete("/", status_code=204)
async def delete_employees(db: AsyncSession = Depends(get_db)):
    """Удаляет всех сотрудников."""
    return await delete_all(db)

@router.get("/search", response_model=EmployeeResponse)
async def search_employee(employee_name: str, db: AsyncSession = Depends(get_db)):
    """Возвращает сотрудника по имени."""
    employee = await get_by_name_fragment(db, employee_name)
    if employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employee