from datetime import date
from pathlib import Path

from services.excel_parser import parse_employee_directory


def test_employee_directory():
    """Тестирование функции parse_employee_directory на корректность парсинга данных из Excel-файла."""
    # Путь к тестовому Excel-файлу с данными сотрудников
    file_path = Path(__file__).parent / "fixtures" / "directory_employees.xlsx"

    # Вызываем функцию парсинга и получаем результат
    result = parse_employee_directory(file_path)
    print(result)

    assert len(result) == 2
    assert result[0] == {
        "full_name": "Иванов Иван Иванович",
        "position": "Механик",
        "contract_number": "1-aa",
        "contract_date": date(2024, 1, 10),
    }