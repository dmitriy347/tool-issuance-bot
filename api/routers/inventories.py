from fastapi import APIRouter, Depends

from sqlalchemy.ext.asyncio import AsyncSession

from api.crud.inventory import get_by_employee_name, create, delete_all
from api.schemas.inventory import InventoryResponse, InventoryCreate
from database import get_db

router = APIRouter(prefix="/inventories", tags=["inventories"])

@router.get("/", response_model=list[InventoryResponse])
async def get_all_inventories(employee_name: str, db: AsyncSession = Depends(get_db)):
    """Возвращает список всего инвентаря."""
    return await get_by_employee_name(db, employee_name)

@router.post("/", response_model=InventoryResponse)
async def create_inventory(inventory_data: InventoryCreate, db: AsyncSession = Depends(get_db)):
    """Создает новый инвентарь"""
    return await create(db, **inventory_data.model_dump())

@router.delete("/", status_code=204)
async def delete_inventories(db: AsyncSession = Depends(get_db)):
    """Удаляет весь инвентарь."""
    return await delete_all(db)
