from fastapi import APIRouter, Depends, UploadFile, File
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from api.crud.employee import get_by_name_fragment
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


@router.post("/generate")
async def get_employee(file: UploadFile = File(...), db: AsyncSession = Depends(get_db)):
    """
    Принимает загруженный файл, читает байты, извлекает фрагменты ФИО сотрудника, ищет сотрудника (сотрудников) в БД,
    получает его инвентарь первого сотрудника, в зависимости от количества сотрудников генерирует DOCX-файл.
    """
    # Читаем байты загруженного файла
    content = await file.read()
    # Парсим файл и получаем фрагменты ФИО сотрудника
    employee = await extract_employee_names(content)
    # Ищем первого сотрудника в БД по фрагменту имени
    emp_1 = await get_by_name_fragment(db, employee["primary"])
    if emp_1 is None:
        return Response(content="Employee not found", status_code=404)

    emp_2 = None
    emp_3 = None
    if employee["second"] is not None:
        emp_2 = await get_by_name_fragment(db, employee["second"])
        if employee["third"] is not None:
            emp_3 = await get_by_name_fragment(db, employee["third"])

    # Получаем инвентарь для первого сотрудника
    inventory = await get_by_employee_name(db, emp_1.full_name)
    if inventory is None:
        return Response(content="Inventory not found", status_code=404)
    
    if emp_2 is None and emp_3 is None:
        docx_content = generate_single(employee_to_dict(emp_1), inventory_to_dict(inventory))
    elif emp_2 and emp_3 is None:
        docx_content = generate_two(employee_to_dict(emp_1), employee_to_dict(emp_2), inventory_to_dict(inventory))
    else:
        docx_content = generate_three(employee_to_dict(emp_1), employee_to_dict(emp_2), employee_to_dict(emp_3), inventory_to_dict(inventory))
    return Response(content=docx_content, media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
