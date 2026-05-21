from os import getenv
from aiogram import Dispatcher, Bot
import asyncio

token = getenv('BOT_TOKEN')
bot = Bot(token=token)
dp = Dispatcher()

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
