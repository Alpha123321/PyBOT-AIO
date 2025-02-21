import aiosqlite
from config import DB_NAME

async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY,
            city TEXT NOT NULL,
            street TEXT NOT NULL,
            square_meters INTEGER NOT NULL
        )""")
        await db.commit()

async def db_add_post(city, street, square_meters):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('INSERT INTO posts (city, street, square_meters) VALUES (?, ?, ?)', (city, street, square_meters))
        await db.commit()

async def get_posts():
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute('SELECT id, city, street, square_meters FROM posts')
        rows = await cursor.fetchall()
        return rows

async def approve_post(post_id):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('UPDATE posts SET approved = 1 WHERE id = ?', (post_id,))
        await db.commit()

async def get_post_by_id(post_id):
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute('SELECT id, city, street, square_meters FROM posts WHERE id = ?', (post_id,))
        post = await cursor.fetchone()
        return post

# Удаление поста (Функция для админов)
async def delete_post(post_id):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('DELETE FROM posts WHERE id = ?', (post_id,))
        await db.commit()