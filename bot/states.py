from aiogram.fsm.state import State, StatesGroup

class UpdateDirectory(StatesGroup):
    """Состояния для обновления справочника."""
    waiting_for_file = State()  # Ожидание загрузки файла пользователем

class NewPeriod(StatesGroup):
    """Состояния для создания нового месяца."""
    waiting_for_period = State()  # Ожидание ввода названия периода пользователем
    waiting_for_file = State()  # Ожидание загрузки файла пользователем

