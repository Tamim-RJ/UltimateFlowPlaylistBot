import asyncio

from aiogram import Bot, Dispatcher

from config import BOT_TOKEN
from database.init_db import create_db
from handlers.admin import router as admin_router
from handlers.request import router as request_router
from handlers.start import router as start_router

bot = Bot(BOT_TOKEN)
dp = Dispatcher()

dp.include_router(start_router)
dp.include_router(request_router)
dp.include_router(admin_router)


async def main():
    await create_db()
    await dp.start_polling(bot)


if __name__ == "__main__":
    print("bot started")
    asyncio.run(main())