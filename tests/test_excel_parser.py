from datetime import date
from pathlib import Path

import pytest

from services.excel_parser import parse_employee_directory, parse_inventory


def test_parse_employee_directory():
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


def test_parse_employee_directory_empty():
    """Тестирование функции parse_employee_directory на корректность парсинга данных из пустого Excel-файла"""
    file_path = Path(__file__).parent / "fixtures" / "directory_employees_1.xlsx"
    with pytest.raises(ValueError):
        parse_employee_directory(file_path)


def test_parse_inventory():
    """Тестирование функции parse_inventory_directory на корректность парсинга данных из Excel-файла."""
    # Путь к тестовому Excel-файлу с данными инвентаря
    file_path = Path(__file__).parent / "fixtures" / "1c_inventories_test.xlsx"

    # Вызываем функцию парсинга и получаем результат
    result = parse_inventory(file_path)
    print(result)
    assert len(result) == 4
    assert result[0] == {
        "employee_name": "Иванов Иван Иванович",
        "tool_name": "Вороток шарнирный",
        "tool_code": "ЦБ000001111",
        "quantity": 2,
        "price": 2500.16,
    }
    assert result[1] == {
        "employee_name": "Сергеев Сергей Сергеевич",
        "tool_name": "Гайковерт",
        "tool_code": "БШ-00004444",
        "quantity": 1,
        "price": 12000,
    }


