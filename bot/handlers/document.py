from os import getenv

import httpx
from aiogram import Router, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, BufferedInputFile

from bot.states import UpdateDirectory, UpdateInventory, GenerateDocument

router = Router()

api_url = getenv("API_URL")

def extract_error_message(e: Exception):
    """
    Извлекает текст ошибки из исключения.
    Если ошибка связана с HTTP-запросом, достает текст ошибки из ответа сервера, иначе - общее сообщение об ошибке.
    """
    if isinstance(e, httpx.HTTPStatusError):
        return e.response.json().get("detail", e.response.text)
    return str(e)


@router.message(UpdateDirectory.waiting_for_file)
async def handle_directory_file(message: Message, bot: Bot, state: FSMContext):
    """
    Обработчик загрузки файла справочника.
    Скачивает файл, отправляет его в API для обработки и очищает состояние.
    """
    if message.document is None:
        await message.answer("Пожалуйста, отправьте файл как документ, не как фото")
        await state.clear()
        return

    async with httpx.AsyncClient() as client:
        try:
            file = await bot.get_file(message.document.file_id)
            file_bytes = await bot.download_file(file.file_path)
            response = await client.post(
                f"{api_url}/api/employees/upload",
                files={"file": (message.document.file_name, file_bytes, "application/octet-stream")},
            )
            response.raise_for_status()
            data = response.json()
            await message.answer(f"Загружено сотрудников: {data['loaded_employees']}")

        # Если ошибка связана с HTTP-запросом, достаем и выводим текст ошибки из ответа сервера, иначе - общее сообщение об ошибке
        except Exception as e:
            await message.answer(f"Ошибка: {extract_error_message(e)}")

        finally:
            await state.clear()  # Очищаем состояние после завершения процесса

@router.message(UpdateInventory.waiting_for_file)
async def handle_new_file_inventory(message: Message, state: FSMContext, bot: Bot):
    """
    Обработчик загрузки файла инвентаря для нового месяца.
    Скачивает файл, отправляет его в API для обработки и очищает состояние.
    """
    if message.document is None:
        await message.answer("Пожалуйста, отправьте файл как документ, не как фото")
        await state.clear()
        return

    async with httpx.AsyncClient() as client:
        try:
            file = await bot.get_file(message.document.file_id)
            file_bytes = await bot.download_file(file.file_path)
            response = await client.post(
                f"{api_url}/api/inventories/upload",
                files={"file": (message.document.file_name, file_bytes, "application/octet-stream")},
            )
            response.raise_for_status()
            data = response.json()
            await message.answer(f"Загружено позиций инвентаря: {data['loaded_inventory']}")

        # Если ошибка связана с HTTP-запросом, достаем и выводим текст ошибки из ответа сервера, иначе - общее сообщение об ошибке
        except Exception as e:
            await message.answer(f"Ошибка: {extract_error_message(e)}")

        finally:
            await state.clear()

@router.message(GenerateDocument.waiting_for_screen)
async def handle_new_file_generate(message: Message, state: FSMContext, bot: Bot):
    """
    Обработчик загрузки скриншота для генерации документа.
    Скачивает файл, отправляет его в API для обработки и очищает состояние.
    """
    async with httpx.AsyncClient() as client:
        try:
            # Получаем последний (с самым большим разрешением) файл из списка фотографий
            file = await bot.get_file(message.photo[-1].file_id)
            file_bytes = await bot.download_file(file.file_path)
            response = await client.post(
                f"{api_url}/api/documents/generate",
                files={"file": ("screen.jpg", file_bytes, "application/octet-stream")},
            )
            response.raise_for_status()
            # Получаем байты сгенерированного DOCX-файла из ответа API
            docx_bytes = response.content
            await message.answer_document(
                BufferedInputFile(docx_bytes, filename="document.docx")
            )

        # Если ошибка связана с HTTP-запросом, выводим текст ответа сервера, иначе - общее сообщение об ошибке
        except Exception as e:
            await message.answer(f"Ошибка: {extract_error_message(e)}")

        finally:
            await state.clear()