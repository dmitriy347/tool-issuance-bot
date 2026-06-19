import os
from os import getenv
from aiogram import Dispatcher, Bot
import asyncio

from aiogram.types import BotCommand

from bot.handlers.commands import router as command_handler
from bot.handlers.document import router as document_handler

token = getenv('BOT_TOKEN')
bot = Bot(token=token)
dp = Dispatcher()
dp.include_router(command_handler)
dp.include_router(document_handler)

async def main():
    os.makedirs("tmp", exist_ok=True)  # Создаём папку tmp, если её нет
    await bot.set_my_commands([
        BotCommand(command="update_directory", description="Загрузить справочник сотрудников"),
        BotCommand(command="update_inventory", description="Загрузить инвентарь для нового месяца"),
        BotCommand(command="generate", description="Сгенерировать документ по скриншоту"),
    ])
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
