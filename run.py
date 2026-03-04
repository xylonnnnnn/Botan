import asyncio

from aiogram import Bot, Dispatcher
from config import TOKEN, DB_URL

from app.handlers import router
from db.database import init_db


async def main():
    await init_db(db_url=DB_URL)
    bot = Bot(token=TOKEN)
    dp = Dispatcher()
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())