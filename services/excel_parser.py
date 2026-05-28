from datetime import datetime
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
