from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from bot.states import UpdateDirectory, NewPeriod

router = Router()

@router.message(Command("update_directory"))
async def cmd_update_directory(message: Message, state: FSMContext):
    """
    Обработчик команды /update_directory.
    Запускает процесс обновления справочника.
    """
    await state.set_state(UpdateDirectory.waiting_for_file)  # Переводим состояние в ожидание загрузки файла
    await message.answer("Отправьте Excel-файл справочника")

@router.message(Command("new_period"))
async def cmd_new_period(message: Message, state: FSMContext):
    """
    Обработчик команды /new_period.
    Запускает процесс создания нового месяца.
    """
    await state.set_state(NewPeriod.waiting_for_period)  # Переводим состояние в ожидание ввода периода
    await message.answer("Введите период в формате ММ.ГГГГ")