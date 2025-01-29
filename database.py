import aiosqlite

DB_NAME = 'quiz_bot.db'

async def create_table():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('''CREATE TABLE IF NOT EXISTS quiz_state
                            (user_id INTEGER PRIMARY KEY, 
                             question_index INTEGER,
                             correct_answers INTEGER DEFAULT 0)''')
        await db.execute('''CREATE TABLE IF NOT EXISTS quiz_results
                            (user_id INTEGER,
                             score INTEGER,
                             last_played TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
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
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('UPDATE quiz_state SET correct_answers = correct_answers + 1 WHERE user_id = ?', (user_id,))
        await db.commit()

async def get_correct_answers(user_id):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute('SELECT correct_answers FROM quiz_state WHERE user_id = ?', (user_id,)) as cursor:
            result = await cursor.fetchone()
            return result[0] if result else 0

async def save_quiz_result(user_id, score):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('INSERT INTO quiz_results (user_id, score) VALUES (?, ?)', (user_id, score))
        await db.commit()

async def get_last_result(user_id):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute('SELECT score, last_played FROM quiz_results WHERE user_id = ? ORDER BY last_played DESC LIMIT 1', (user_id,)) as cursor:
            return await cursor.fetchone()