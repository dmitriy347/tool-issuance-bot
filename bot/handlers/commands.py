from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from bot.states import UpdateDirectory, UpdateInventory, GenerateDocument

router = Router()

@router.message(Command("update_directory"))
async def cmd_update_directory(message: Message, state: FSMContext):
    """
    Обработчик команды /update_directory.
    Запускает процесс обновления справочника.
    """
    await state.set_state(UpdateDirectory.waiting_for_file)  # Переводим состояние в ожидание загрузки файла
    await message.answer("Отправьте Excel-файл справочника")

@router.message(Command("update_inventory"))
async def cmd_new_period(message: Message, state: FSMContext):
    """
    Обработчик команды /update_inventory.
    Запускает процесс обновления инвентаря.
    """
    await state.set_state(UpdateInventory.waiting_for_file)  # Переводим состояние в ожидание загрузки файла
    await message.answer("Отправьте Excel-файл инвентаря для нового месяца")

@router.message(Command("generate"))
async def cmd_generate(message: Message, state: FSMContext):
    """
    Обработчик команды /generate.
    Запускает процесс генерации документа.
    """
    await state.set_state(GenerateDocument.waiting_for_screen)  # Переводим состояние в ожидание загрузки скриншота
    await message.answer("Отправьте скриншот с данными для генерации документа")