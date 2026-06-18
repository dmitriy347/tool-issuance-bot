from fastapi import APIRouter, Depends, UploadFile, File, HTTPException

from sqlalchemy.ext.asyncio import AsyncSession

from api.crud.inventory import get_by_employee_name, create, delete_all
from api.schemas.inventory import InventoryResponse, InventoryCreate
from database import get_db
from services.excel_parser import parse_inventory

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

@router.post("/upload")
async def upload_inventories(file: UploadFile = File(...), db: AsyncSession = Depends(get_db)):
    """
    Загружает Excel-файл целиком, парсит и сохраняет инвентарь БД.
    Перед загрузкой нового файла удаляет все существующие записи об инвентаре.
    Возвращает количество загруженных записей инвентаря.
    """
    content = await file.read()
    try:
        inventories = parse_inventory(content)
    # Если файл повреждён или не является Excel-файлом, parse_employee_directory выбросит ValueError
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Удаляем все существующие записи об инвентаре
    await delete_all(db)
    for inventory in inventories:
        await create(db, **inventory)
    return {"loaded_inventory": len(inventories)}