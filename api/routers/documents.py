import httpx
import json
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from fastapi.responses import Response
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from api.crud.employee import get_by_name_fragment, EmployeeError
from api.crud.inventory import get_by_employee_name
from database import get_db
from models.employee import Employee
from models.inventory import Inventory
from services.ai_extractor import extract_employee_names
from services.docx_generator import generate_single, generate_two, generate_three

router = APIRouter(prefix="/documents", tags=["documents"])

def employee_to_dict(employee: Employee) -> dict:
    """Преобразует объект Employee в словарь."""
    employee_dict = {
        "full_name": employee.full_name,
        "position": employee.position,
        "contract_number": employee.contract_number,
        "contract_date": employee.contract_date,
        "document_type": employee.document_type,
        "id_series": employee.id_series,
        "id_number": employee.id_number,
        "id_issued_date": employee.id_issued_date,
        "issued_by": employee.issued_by,
        "address": employee.address,
    }
    return employee_dict

def inventory_to_dict(inventory: list[Inventory]) -> list[dict]:
    """Преобразует список объектов Inventory в список словарей."""
    inventory_list = []
    for item in inventory:
        inventory_dict = {
            "tool_name": item.tool_name,
            "tool_code": item.tool_code,
            "quantity": item.quantity,
            "price": item.price,
        }
        inventory_list.append(inventory_dict)
    return inventory_list


async def _find_employee_or_404(db: AsyncSession, name_fragment: str) -> Employee:
    """Ищет сотрудника по фрагменту имени в БД. Если не найден, возвращает 404."""
    try:
        employee = await get_by_name_fragment(db, name_fragment)
    except EmployeeError as e:
        raise HTTPException(status_code=409, detail=str(e))
    if employee is None:
        raise HTTPException(status_code=404, detail=f"Сотрудник не найден: {name_fragment}")
    return employee


@router.post("/generate")
async def generate_document(file: UploadFile = File(...), db: AsyncSession = Depends(get_db)):
    """
    Принимает скриншот, извлекает фрагменты ФИО сотрудника(ов) через AI, ищет сотрудника(ов) в БД,
    получает инвентарь первого сотрудника, генерирует DOCX-документ по шаблону (на 1/2/3 сотрудников).
    """
    # Читаем байты загруженного файла
    content = await file.read()

    # Парсим файл и извлекаем фрагменты ФИО из скриншота
    try:
        names = await extract_employee_names(content)

    # Если Groq API вернул ошибку (неверный API-ключ, превышен лимит запросов)
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=502, detail=f"Ошибка сервиса распознавания: {str(e)}")
    # Если у Groq API истек тайм-аут
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Истекло время ожидания сервиса распознавания")
    # Если модель вернула некорректный JSON
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=502, detail=f"Не удалось распознать данные: {str(e)}")
    # Если данные не соответствуют Pydantic-схеме ExtractedNames
    except ValidationError as e:
        raise HTTPException(status_code=502, detail=f"Ошибка валидации данных: {str(e)}")

    # Ищем сотрудников в БД по фрагментам имени
    employees = [await _find_employee_or_404(db, names.primary)]
    if names.second is not None:
        employees.append(await _find_employee_or_404(db, names.second))
    if names.third is not None:
        employees.append(await _find_employee_or_404(db, names.third))

    # Получаем инвентарь для первого сотрудника (т.к. в 1C он всегда привязан к первому сотруднику).
    inventory = await get_by_employee_name(db, employees[0].full_name)

    # Если инвентарь не найден [пустой список], возвращаем 404.
    if not inventory:
        raise HTTPException(status_code=404, detail="Инвентарь по сотруднику не найден")

    inventory_dicts = inventory_to_dict(inventory)
    employee_dicts = [employee_to_dict(e) for e in employees]

    try:
        if len(employee_dicts) == 1:
            docx_content = generate_single(employee_dicts[0], inventory_dicts)
        elif len(employee_dicts) == 2:
            docx_content = generate_two(employee_dicts[0], employee_dicts[1], inventory_dicts)
        else:
            docx_content = generate_three(employee_dicts[0], employee_dicts[1], employee_dicts[2], inventory_dicts)
    except FileNotFoundError as e:
        raise HTTPException(status_code=500, detail=str(e))

    return Response(
        content=docx_content,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )