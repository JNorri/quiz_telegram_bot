from aiogram import Router, types
from aiogram.filters import Command
from database import get_user_stats

router = Router()

@router.message(Command("stats"))
async def cmd_stats(message: types.Message):
    user_id = message.from_user.id
    stats = await get_user_stats(user_id)
    
    if not stats['total_quizzes']:
        await message.answer("Вы еще не прошли ни одного квиза!")
        return

    response = [
        "📊 <b>Ваша статистика:</b>",
        f"• Всего квизов: {stats['total_quizzes']}",
        f"• Средний результат: {stats['mode_score']}",
        f"• Лучший результат: {stats['best_score']} ({stats['best_percent']:.1f}%)"
    ]

    if stats['quizzes']:
        last_quiz = stats['quizzes'][0]
        last_percent = (last_quiz[1]/last_quiz[2])*100
        response.extend([
            "\n📅 <b>Последняя попытка:</b>",
            f"{last_quiz[0]}: {last_percent:.1f}% ({last_quiz[1]}/{last_quiz[2]})"
        ])

    await message.answer("\n".join(response), parse_mode="HTML")
