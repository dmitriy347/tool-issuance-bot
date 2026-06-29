from datetime import date
from decimal import Decimal
from io import BytesIO
from pathlib import Path
from docxtpl import DocxTemplate

TEMPLATES_DIR = Path(__file__).parent.parent / "templates"


def _format_date(d: date) -> str:
    """Преобразует date в строку вида '10 мая 2026'."""
    months = {1: "января", 2: "февраля", 3: "марта", 4: "апреля", 5: "мая", 6: "июня",
              7: "июля", 8: "августа", 9: "сентября", 10: "октября", 11: "ноября", 12: "декабря"}
    result = f"{d.day} {months[d.month]} {d.year}"
    return result

def _format_item_price(price: Decimal) -> str:
    """Преобразует Decimal-цену в строку вида '1 500,00'."""
    price_str = f"{price:,.2f}".replace(",", " ").replace(".", ",")
    return price_str

def _build_employee_context(employee: dict) -> dict:
    """Формирует словарь с данными сотрудника в формате, удобном для шаблона."""
    emp = {
        "full_name": employee["full_name"],
        "position": employee["position"],
        "contract_date": _format_date(employee["contract_date"]),
        "contract_number": employee["contract_number"],
        "document_type": employee["document_type"],
        "id_series": employee["id_series"],
        "id_number": employee["id_number"],
        "id_issued_date": _format_date(employee["id_issued_date"]),
        "issued_by": employee["issued_by"],
        "address": employee["address"],
    }
    return emp

def _build_items_context(items: list[dict]) -> list[dict]:
    """Формирует список словарей с данными об инвентаре в формате, удобном для шаблона."""
    items_str = []
    for item in items:
        item_str = {
            "tool_name": item["tool_name"],
            "tool_code": item["tool_code"],
            "quantity": item["quantity"],
            "price": _format_item_price(item["price"])
        }
        items_str.append(item_str)
    return items_str


def _render(template_path: Path, context: dict) -> bytes:
    """Рендерит шаблон с контекстом и возвращает байты"""
    try:
        template = DocxTemplate(template_path)  # Загружаем шаблон
    except FileNotFoundError:
        raise FileNotFoundError(f"Шаблон для генерации документа не найден: {template_path}")
    template.render(context)  # Заполняем шаблон данными из БД
    buffer = BytesIO()  # Создаем буфер для сохранения сгенерированного документа
    template.save(buffer)  # Сохраняем сгенерированный документ в буфер
    return buffer.getvalue()  # Возвращаем байты документа для отправки

def generate_single(employee: dict, items: list[dict]) -> bytes:
    """Генерирует документ для одного сотрудника."""
    context = {
        # Распаковываем словарь с данными сотрудника в контекст, чтобы его ключи стали ключами контекста
        **_build_employee_context(employee),
        "items": _build_items_context(items)
    }
    template_path = TEMPLATES_DIR / "single_employee.docx"
    return _render(template_path, context)

def generate_two(employee_1: dict, employee_2: dict, items: list[dict]) -> bytes:
    """Генерирует документ для двух сотрудников."""
    # Перебираем все пары ключ-значение из словаря, и добавляем суффикс к каждому ключу, чтобы отличать сотрудников
    emp_1 = {f"{key}_1": value for key, value in _build_employee_context(employee_1).items()}
    emp_2 = {f"{key}_2": value for key, value in _build_employee_context(employee_2).items()}

    context = {
        **emp_1,
        **emp_2,
        "items": _build_items_context(items)
    }
    template_path = TEMPLATES_DIR / "two_employees.docx"
    return _render(template_path, context)

def generate_three(employee_1: dict, employee_2: dict, employee_3: dict, items: list[dict]) -> bytes:
    """Генерирует документ для трех сотрудников."""
    emp_1 = {f"{key}_1": value for key, value in _build_employee_context(employee_1).items()}
    emp_2 = {f"{key}_2": value for key, value in _build_employee_context(employee_2).items()}
    emp_3 = {f"{key}_3": value for key, value in _build_employee_context(employee_3).items()}

    context = {
        **emp_1,
        **emp_2,
        **emp_3,
        "items": _build_items_context(items)
    }
    template_path = TEMPLATES_DIR / "three_employees.docx"
    return _render(template_path, context)
