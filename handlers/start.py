from aiogram import Router, types
from aiogram.filters import Command
from aiogram.utils.keyboard import ReplyKeyboardBuilder

router = Router()

router = Router()

@router.message(Command("start"))
async def cmd_start(message: types.Message):
    builder = ReplyKeyboardBuilder()
    builder.row(
        types.KeyboardButton(text="/start 🚀"),
        types.KeyboardButton(text="/quiz 📝"),
        types.KeyboardButton(text="/stats 📊")
    )
    builder.row(
        types.KeyboardButton(text="/help ❓")
    )
    
    await message.answer(
        "📚 <b>Добро пожаловать в Python Quiz Bot!</b>\n\n"
        "Выберите действие:",
        reply_markup=builder.as_markup(resize_keyboard=True),
        parse_mode="HTML"
    )
    

# Храним команды в виде словаря
commands = {
    "/start": "Начать взаимодействие",
    "/quiz": "Начать квиз",
    "/stats": "Показать статистику",
    "/help": "Показать таблицу команд бота"
}

@router.message(Command("help"))
async def cmd_help(message: types.Message):
    # Вычисляем максимальные ширины для каждого столбца
    col1_width = max(len(str(i)) for i in range(1, len(commands) + 1))
    col2_width = max(len(cmd) for cmd in commands.keys())
    col3_width = max(len(desc) for desc in commands.values())

    # Учитываем ширину заголовков
    col1_width = max(col1_width, len("№"))
    col2_width = max(col2_width, len("Команда"))
    col3_width = max(col3_width, len("Описание"))
    
    # Заголовок таблицы
    table = f"| {'№'.ljust(col1_width)} | {'Команда'.ljust(col2_width)} | {'Описание'.ljust(col3_width)} |\n"
    table += f"|{'-' * (col1_width + 2)}|{'-' * (col2_width + 2)}|{'-' * (col3_width + 2)}|\n"

    # Строки с командами
    for i, (command, description) in enumerate(commands.items(), start=1):
        table += f"| {str(i).ljust(col1_width)} | {command.ljust(col2_width)} | {description.ljust(col3_width)} |\n"

    # Отправка отформатированной таблицы
    await message.answer(f"```\n{table}\n```", parse_mode="MarkdownV2")
