from aiogram import Router, types, F
from aiogram.utils.keyboard import InlineKeyboardBuilder
from database import (update_quiz_index, 
                     increment_correct_answers, 
                     get_quiz_index, 
                     save_quiz_result, 
                     get_correct_answers)
from data.quiz_data import quiz_data
from keyboards import generate_options_keyboard

router = Router()

@router.callback_query(F.data.startswith("answer_"))
async def answer_handler(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    data_parts = callback.data.split('_')
    selected_option = int(data_parts[1])
    correct_option = int(data_parts[2])

    await callback.bot.edit_message_reply_markup(
        chat_id=user_id,
        message_id=callback.message.message_id,
        reply_markup=None
    )

    current_question_index = await get_quiz_index(user_id)
    question_data = quiz_data[current_question_index]
    selected_text = question_data['options'][selected_option]
    correct_text = question_data['options'][correct_option]

    if selected_option == correct_option:
        await increment_correct_answers(user_id)
        await callback.message.answer(f"✅ Вы выбрали: {selected_text}. Верно!")
    else:
        await callback.message.answer(f"❌ Вы выбрали: {selected_text}. Неверно. Правильный ответ: {correct_text}")

    current_question_index += 1
    await update_quiz_index(user_id, current_question_index)

    if current_question_index < len(quiz_data):
        await get_question(callback.message, user_id)
    else:
        correct_answers = await get_correct_answers(user_id)
        await save_quiz_result(user_id, correct_answers)
        await callback.message.answer(f"🏁 Квиз завершен! Правильных ответов: {correct_answers} из {len(quiz_data)}")

async def get_question(message, user_id):
    current_question_index = await get_quiz_index(user_id)
    question_data = quiz_data[current_question_index]
    keyboard = generate_options_keyboard(
        question_data['options'],
        question_data['correct_option']
    )
    await message.answer(f"{question_data['question']}", reply_markup=keyboard)