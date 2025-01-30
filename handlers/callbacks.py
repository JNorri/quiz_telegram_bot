from aiogram import Router, types, F
import aiosqlite
from database import DB_NAME  
from database import (update_quiz_index, get_quiz_index, save_quiz_result)
from data.quiz_data import quiz_data
from keyboards import generate_options_keyboard

router = Router()

# Создаем словарь для хранения правильных ответов для каждого пользователя
user_correct_answers = {}

@router.callback_query(F.data.startswith("answer_"))
async def answer_handler(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    data_parts = callback.data.split('_')
    selected_option = int(data_parts[1])
    correct_option = int(data_parts[2])

    # Локальное хранилище правильных ответов
    if user_id not in user_correct_answers:
        user_correct_answers[user_id] = 0

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
        user_correct_answers[user_id] += 1  # Инкрементируем локально
        await callback.message.answer(f"✅ Вы выбрали: {selected_text}. Верно!")
    else:
        await callback.message.answer(f"❌ Вы выбрали: {selected_text}. Неверно. Правильный ответ: {correct_text}")

    current_question_index += 1
    await update_quiz_index(user_id, current_question_index)

    if current_question_index < len(quiz_data):
        await get_question(callback.message, user_id)
    else:
        # В конце квиза сохраняем результат в базу данных
        correct_answers = user_correct_answers.get(user_id, 0)
        total_questions = len(quiz_data)
        await save_quiz_result(user_id, correct_answers, total_questions)
        await callback.message.answer(f"🏁 Квиз завершен! Правильных ответов: {correct_answers}/{total_questions}")
        await reset_counter(user_id)
        

async def get_question(message, user_id):
    current_question_index = await get_quiz_index(user_id)
    question_data = quiz_data[current_question_index]
    keyboard = generate_options_keyboard(
        question_data['options'],
        question_data['correct_option']
    )
    await message.answer(f"{question_data['question']}", reply_markup=keyboard)
    
async def reset_counter(user_id):
    # Сбрасываем счетчик в БД
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            'UPDATE quiz_state SET correct_answers = 0 WHERE user_id = ?', 
            (user_id,)
        )
        await db.commit()
    
    # Очищаем локальное хранилище
    if user_id in user_correct_answers:
        del user_correct_answers[user_id]