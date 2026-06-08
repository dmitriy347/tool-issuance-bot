from aiogram import Router, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from datetime import datetime

from bot.states import UpdateDirectory, NewPeriod
from services.excel_parser import parse_employee_directory, parse_inventory

router = Router()

@router.message(UpdateDirectory.waiting_for_file)
async def handle_directory_file(message: Message, bot: Bot, state: FSMContext):
    """
    Обработчик загрузки файла справочника.
    Скачивает файл, парсит его, возвращает количество сотрудников в справочнике и очищает состояние.
    """
    try:
        file = await bot.get_file(message.document.file_id)
        await bot.download_file(file.file_path, destination="tmp/directory.xlsx")
        result = parse_employee_directory("tmp/directory.xlsx")  # Парсим файл справочника
        await message.answer(f"Загружено сотрудников: {len(result)}")
    except Exception as e:
        await message.answer(f"Произошла ошибка при обработке файла: {str(e)}")
    finally:
        await state.clear()  # Очищаем состояние после завершения процесса



@router.message(NewPeriod.waiting_for_period)
async def handle_new_period(message: Message, state: FSMContext):
    """
    Обработчик ввода периода для нового месяца.
    Сохраняет период в состоянии и переводит состояние в ожидание загрузки файла для нового месяца.
    """
    try:
        datetime.strptime(message.text,"%m.%Y")  # Проверяем, что введённый период соответствует формату ММ.ГГГГ
    except ValueError:
        await message.answer("Неверный формат периода. Пожалуйста, введите период в формате ММ.ГГГГ")
        return  # Не изменяем состояние, пользователь вводит период снова
    await state.update_data(period=message.text)  # Сохраняем введённый период в состоянии
    await state.set_state(NewPeriod.waiting_for_file)  # Переводим состояние в ожидание загрузки файла
    await message.answer("Отправьте Excel-файл инвентаря")

@router.message(NewPeriod.waiting_for_file)
async def handle_new_file_inventory(message: Message, state: FSMContext, bot: Bot):
    """
    Обработчик загрузки файла инвентаря для нового месяца.
    Скачивает файл, парсит его с учётом сохранённого периода, возвращает количество записей инвентаря и очищает состояние.
    """
    data = await state.get_data()  # Получаем сохранённые данные из состояния
    period = datetime.strptime(data["period"],"%m.%Y").date()  # Получаем период из сохранённых данных и преобразуем его в объект date
    try:
        file = await bot.get_file(message.document.file_id)
        await bot.download_file(file.file_path, destination="tmp/inventory.xlsx")
        result = parse_inventory("tmp/inventory.xlsx", period)
        await message.answer(f"Загружено записей: {len(result)}")
    except Exception as e:
        await message.answer(f"Произошла ошибка при обработке файла: {str(e)}")
    finally:
        await state.clear()