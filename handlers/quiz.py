from aiogram import Router, types, F
import aiosqlite
from database import DB_NAME  
from aiogram.filters import Command
from database import get_quiz_index
from keyboards import generate_options_keyboard
from data.quiz_data import quiz_data


router = Router()

@router.message(Command("quiz"))
@router.message(F.text == "Начать игру")
async def cmd_quiz(message: types.Message):
    await message.answer("Давайте начнем квиз!")
    await new_quiz(message)


async def new_quiz(message):
    user_id = message.from_user.id

    # Cуществование записи
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('''
            INSERT OR IGNORE INTO quiz_state 
            (user_id, question_index, correct_answers) 
            VALUES (?, 0, 0)
        ''', (user_id,))
        await db.execute('''
            UPDATE quiz_state 
            SET question_index = 0, correct_answers = 0 
            WHERE user_id = ?
        ''', (user_id,))
        await db.commit()

    await get_question(message, user_id)



async def get_question(message, user_id):
    current_question_index = await get_quiz_index(user_id)
    question_data = quiz_data[current_question_index]
    keyboard = generate_options_keyboard(
        question_data['options'],
        question_data['correct_option']
    )
    await message.answer(f"{question_data['question']}", reply_markup=keyboard)