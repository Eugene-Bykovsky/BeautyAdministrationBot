import asyncio
from environs import Env
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from app.handlers import (start_router, master_router, salon_router,
                          phone_router)


async def main():
    env = Env()
    env.read_env()
    TELEGRAM_BOT_TOKEN = env.str('TELEGRAM_BOT_TOKEN')
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(start_router)
    dp.include_router(salon_router)
    dp.include_router(master_router)
    dp.include_router(phone_router)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
