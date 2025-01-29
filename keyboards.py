from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import types

def generate_options_keyboard(answer_options, correct_option):
    builder = InlineKeyboardBuilder()
    for index, option in enumerate(answer_options):
        builder.add(types.InlineKeyboardButton(
            text=option,
            callback_data=f"answer_{index}_{correct_option}")
        )
    builder.adjust(4)
    return builder.as_markup()