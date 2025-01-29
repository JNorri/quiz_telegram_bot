import asyncio
import logging
from aiogram import Bot, Dispatcher
from handlers.start import cmd_start
from handlers.quiz import cmd_quiz, new_quiz
from handlers.callbacks import answer_handler
from database import create_table

logging.basicConfig(level=logging.INFO)
API_TOKEN = 'YOUR_BOT_TOKEN'
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

dp.include_router(cmd_start.router)
dp.include_router(cmd_quiz.router)
dp.include_router(answer_handler.router)

async def main():
    await create_table()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())