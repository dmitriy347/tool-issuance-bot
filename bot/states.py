from aiogram.fsm.state import State, StatesGroup

class UpdateDirectory(StatesGroup):
    """Состояния для обновления справочника."""
    waiting_for_file = State()  # Ожидание загрузки файла пользователем

class UpdateInventory(StatesGroup):
    """Состояния для обновления инвентаря."""
    waiting_for_file = State()  # Ожидание загрузки файла пользователем

class GenerateDocument(StatesGroup):
    """Состояния для генерации документа."""
    waiting_for_screen = State()  # Ожидание загрузки скриншота пользователем
