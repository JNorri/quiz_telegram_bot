import aiosqlite
import os
import logging

logging.basicConfig(level=logging.DEBUG)
DB_NAME = 'quiz_bot.db'

if os.path.exists("quiz_bot.db"):
    os.remove("quiz_bot.db")


async def create_table():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('''DROP TABLE IF EXISTS quiz_state;''')
        await db.execute('''CREATE TABLE quiz_state (
                                user_id INTEGER PRIMARY KEY,
                                question_index INTEGER,
                                correct_answers INTEGER DEFAULT 0);''')
        await db.execute('''DROP TABLE IF EXISTS quiz_results;''')
        await db.execute('''CREATE TABLE IF NOT EXISTS quiz_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    score INTEGER,
    total_questions INTEGER,
    last_played TIMESTAMP DEFAULT CURRENT_TIMESTAMP);''')
        await db.commit()



async def get_quiz_index(user_id):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute('SELECT question_index FROM quiz_state WHERE user_id = ?', (user_id,)) as cursor:
            result = await cursor.fetchone()
            return result[0] if result else 0

async def update_quiz_index(user_id, index):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('INSERT OR REPLACE INTO quiz_state (user_id, question_index) VALUES (?, ?)', (user_id, index))
        await db.commit()

async def increment_correct_answers(user_id):
    logging.debug(f"Попытка увеличить correct_answers для пользователя {user_id}")
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            'UPDATE quiz_state SET correct_answers = correct_answers + 1 WHERE user_id = ?', 
            (user_id,)
        )
        await db.commit()
    logging.debug(f"Увеличено количество правильных ответов для пользователя {user_id}")


async def get_correct_answers(user_id):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute('SELECT correct_answers FROM quiz_state WHERE user_id = ?', (user_id,)) as cursor:
            result = await cursor.fetchone()
            logging.debug(f"Количество правильных ответов для пользователя {user_id}: {result[0] if result else 0}")
            return result[0] if result else 0


async def save_quiz_result(user_id, score, total_questions):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('''
            INSERT INTO quiz_results 
            (user_id, score, total_questions) 
            VALUES (?, ?, ?)
        ''', (user_id, score, total_questions))
        await db.commit()
    logging.debug(f"Результат сохранён: user_id={user_id}, score={score}, total_questions={total_questions}")

async def get_last_result(user_id):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute('SELECT score, last_played FROM quiz_results WHERE user_id = ? ORDER BY last_played DESC LIMIT 1', (user_id,)) as cursor:
            return await cursor.fetchone()

async def get_user_stats(user_id):
    async with aiosqlite.connect(DB_NAME) as db:
        # Основная статистика
        async with db.execute('''
            SELECT 
                COUNT(*) as total_quizzes,
                SUM(score) as total_correct,
                SUM(total_questions) as total_questions
            FROM quiz_results 
            WHERE user_id = ?
        ''', (user_id,)) as cursor:
            total_stats = await cursor.fetchone()

        # Находим моду (самое частое количество правильных ответов)
        async with db.execute('''
            SELECT score, COUNT(*) as freq 
            FROM quiz_results 
            WHERE user_id = ? 
            GROUP BY score 
            ORDER BY freq DESC, score DESC 
            LIMIT 1
        ''', (user_id,)) as cursor:
            mode_row = await cursor.fetchone()
            mode_score = mode_row[0] if mode_row else 0

        # Лучший результат
        async with db.execute('''
            SELECT MAX(score), MAX(CAST(score AS FLOAT)/total_questions)*100 
            FROM quiz_results 
            WHERE user_id = ?
        ''', (user_id,)) as cursor:
            best_row = await cursor.fetchone()
            best_score = best_row[0] if best_row else 0
            best_percent = best_row[1] if best_row else 0

        # Статистика по попыткам
        async with db.execute('''
            SELECT 
                strftime('%d.%m.%Y %H:%M', last_played),
                score,
                total_questions
            FROM quiz_results 
            WHERE user_id = ? 
            ORDER BY last_played DESC
        ''', (user_id,)) as cursor:
            quizzes = await cursor.fetchall()

        return {
            'total_quizzes': total_stats[0] if total_stats else 0,
            'mode_score': mode_score,
            'best_score': best_score,
            'best_percent': best_percent or 0,
            'quizzes': quizzes
        }
