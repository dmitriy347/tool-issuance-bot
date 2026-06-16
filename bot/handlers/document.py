from os import getenv

import httpx
from aiogram import Router, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from bot.states import UpdateDirectory, UpdateInventory
from services.excel_parser import parse_employee_directory, parse_inventory

router = Router()

api_url = getenv("API_URL")

@router.message(UpdateDirectory.waiting_for_file)
async def handle_directory_file(message: Message, bot: Bot, state: FSMContext):
    """
    Обработчик загрузки файла справочника.
    Скачивает файл, парсит его, возвращает количество сотрудников в справочнике и очищает состояние.
    """
    async with httpx.AsyncClient() as client:
        try:
            # Перед загрузкой нового файла удаляем все существующие записи о сотрудниках через API
            response = await client.delete(f"{api_url}/api/employees/")
            response.raise_for_status()

            file = await bot.get_file(message.document.file_id)
            await bot.download_file(file.file_path, destination="tmp/directory.xlsx")
            result = parse_employee_directory("tmp/directory.xlsx")  # Парсим файл справочника

            # Отправляем каждого сотрудника в API
            for employee in result:
                # Преобразуем дату в строку в формате ISO, чтобы её можно было отправить в JSON
                employee["contract_date"] = employee["contract_date"].isoformat()
                response = await client.post(f"{api_url}/api/employees/", json=employee)
                response.raise_for_status()

            await message.answer(f"Загружено сотрудников: {len(result)}")
        except Exception as e:
            await message.answer(f"Произошла ошибка при обработке файла: {str(e)}")
        finally:
            await state.clear()  # Очищаем состояние после завершения процесса

@router.message(UpdateInventory.waiting_for_file)
async def handle_new_file_inventory(message: Message, state: FSMContext, bot: Bot):
    """
    Обработчик загрузки файла инвентаря для нового месяца.
    Скачивает файл, парсит его, возвращает количество записей инвентаря и очищает состояние.
    """
    async with httpx.AsyncClient() as client:
        try:
            # Перед загрузкой нового файла удаляем все существующие записи инвентаря через API
            response = await client.delete(f"{api_url}/api/inventories/")
            response.raise_for_status()

            file = await bot.get_file(message.document.file_id)
            await bot.download_file(file.file_path, destination="tmp/inventory.xlsx")
            result = parse_inventory("tmp/inventory.xlsx")

            # Отправляем каждую запись инвентаря в API
            for inventory in result:
                response = await client.post(f"{api_url}/api/inventories/", json=inventory)
                response.raise_for_status()

            await message.answer(f"Загружено записей: {len(result)}")
        except Exception as e:
            await message.answer(f"Произошла ошибка при обработке файла: {str(e)}")
        finally:
            await state.clear()