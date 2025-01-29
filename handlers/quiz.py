from aiogram import Router, types, F
from aiogram.filters import Command
from database import get_quiz_index, update_quiz_index, get_correct_answers, save_quiz_result
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
    await update_quiz_index(user_id, 0)
    await get_question(message, user_id)

async def get_question(message, user_id):
    current_question_index = await get_quiz_index(user_id)
    question_data = quiz_data[current_question_index]
    keyboard = generate_options_keyboard(
        question_data['options'],
        question_data['correct_option']
    )
    await message.answer(f"{question_data['question']}", reply_markup=keyboard)