from datetime import datetime, date

from openpyxl import load_workbook


def parse_employee_directory(file_path: str) -> list[dict]:
    """Парсит Excel-файл с данными сотрудников и возвращает список словарей с данными каждого сотрудника."""
    # Загружаем Excel-файл в режиме "только для чтения", для экономии памяти (при работе с большими файлами)
    try:
        wb = load_workbook(filename=file_path, read_only=True)
        ws = wb.active  # Получаем активный лист

        employees = []
        header_found = False  # Флаг для определения, когда найдены данные сотрудников

        for row in ws.iter_rows(values_only=True): # Итерируемся по строкам листа, получаем только значения ячеек
            if row[0] == "Сотрудник":  # Ищем строку, где первый столбец == "Сотрудник", чтобы начать парсинг данных
                header_found = True  # Устанавливаем флаг, что заголовок найден, и следующие строки будут данными сотрудников
                continue

            if header_found:
                if row[0] is not None: # Если первый столбец не пустой, считаем, что это данные сотрудника
                    employee = {
                        # Убираем лишние пробелы и заменяем неразрывные пробелы на обычные, чтобы данные были чистыми
                        "full_name": row[0].strip().replace("\xa0", " "),
                        "position": row[12].strip().replace("\xa0", " "),
                        "contract_number": row[3].strip().replace("\xa0", " "),
                        "contract_date": datetime.strptime(row[8], "%d.%m.%Y").date(), # Преобразуем строку с датой в объект date, предполагая формат "день.месяц.год"
                    }
                    employees.append(employee)
                else:  # Иначе, считаем, что данные сотрудников закончились
                    break
    finally:
        wb.close()
    return employees







def employee_name(value: str) -> bool:
    """
    Проверяет, является ли значение ФИО сотрудника.
    Если строка содержит 3 слова, каждое из которых начинается с заглавной буквы, то это имя сотрудника.
    """
    parts = value.split()
    result = len(parts) == 3 and all(p and p[0].isupper() for p in parts)
    return result


def inventory_code(value: str) -> bool:
    """
    Проверяет, является ли значение кодом инвентаря.
    """
    return value.startswith("ЦБ") or value.startswith("БШ")


def parse_inventory(file_path: str | bytes) -> list[dict]:
    """Парсит Excel-файл с данными инвентаря и возвращает список словарей с данными каждого предмета."""
    try:
        wb = load_workbook(filename=file_path, read_only=True)
        ws = wb.active

        current_employee = None  # Храним текущего сотрудника
        current_tool_code = None  # Храним текущий код инструмента
        current_tool_name = None  # Храним текущее название инструмента
        price = None  # Храним цену текущего инструмента
        inventories = []

        for row in ws.iter_rows(values_only=True):
            if row[0] is None or row[1] == "Кол.":
                if current_tool_code and price is not None:
                    quantity = row[4]
                    inventories.append({
                        "employee_name": current_employee,
                        "tool_name": current_tool_name,
                        "tool_code": current_tool_code,
                        "quantity": quantity,
                        "price": price,
                    })
                    current_tool_code = None  # Сбрасываем
                    price = None
                continue

            # Убираем лишние пробелы и заменяем неразрывные пробелы на обычные, чтобы данные были чистыми
            value = str(row[0]).strip().replace("\xa0", " ")

            if value == "МЦ.04":
                continue

            # Если встречаем ФИО сотрудника
            elif employee_name(value):
                current_employee = value

            # Если встречаем код инвентаря
            elif inventory_code(value):
                current_tool_code = value
                price = row[4]

            # Если есть ФИО сотрудника, то следующая строка - это название инструмента
            elif current_employee:
                current_tool_name = value
    finally:
        wb.close()
    return inventories