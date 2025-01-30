import asyncio
import logging
from aiogram import Bot, Dispatcher
from handlers.start import router as start_router
from handlers.quiz import router as quiz_router
from handlers.callbacks import router as callbacks_router
from database import create_table
from handlers.stats import router as stats_router

logging.basicConfig(level=logging.INFO)
API_TOKEN = 'YOUR_API_TOKEN'
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

dp.include_router(start_router)
dp.include_router(quiz_router)
dp.include_router(callbacks_router)
dp.include_router(stats_router)

async def main():
    await create_table()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())