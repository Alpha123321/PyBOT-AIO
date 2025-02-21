from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
import logging
from config import API_TOKEN
from states import PostForm
import db

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    await message.reply("Приветствую! Используй /new_post для добавления нового поста.")

@dp.message_handler(commands=['new_post'], state='*')
async def new_post_start(message: types.Message):
    await PostForm.waiting_for_city.set()
    await message.reply("Введите город:")

@dp.message_handler(state=PostForm.waiting_for_city)
async def process_city(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['city'] = message.text
    await PostForm.next()
    await message.reply("Введите улицу:")

@dp.message_handler(state=PostForm.waiting_for_street)
async def process_street(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['street'] = message.text
    await PostForm.next()
    await message.reply("Введите количество квадратных метров:")

@dp.message_handler(state=PostForm.waiting_for_square_meters)
async def process_square_meters(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['square_meters'] = message.text
    await db.db_add_post(data['city'], data['street'], data['square_meters'])
    await state.finish()
    await message.reply("Ваш пост успешно добавлен.")

async def on_startup(_):
    # Инициализация базы данных при старте бота
    await db.init_db()

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)

ADMINS = ['ValeryPyao']  # Замените на реальный ID администратора

def is_admin(user_id):
    return str(user_id) in ADMINS

@dp.message_handler(commands=['admin_posts'], user_id=ADMINS)
async def list_posts(message: types.Message):
    posts = await db.get_posts()
    if not posts:
        await message.answer("Постов пока нет.")
        return

    for post in posts:
        post_id, city, street, square_meters = post
        # В сообщении используется Markdown, для форматирования текста
        await message.answer(f"`ID: {post_id}`\nГород: {city}\nУлица: {street}\nПлощадь: {square_meters} кв. м.", parse_mode="Markdown")

@dp.message_handler(commands=['approve'], user_id=ADMINS)
async def approve_post_command(message: types.Message):
    post_id = message.get_args()
    await db.approve_post(post_id)
    await message.answer(f"Пост {post_id} одобрен.")

@dp.message_handler(commands=['delete_post'], user_id=ADMINS)
async def delete_post_command(message: types.Message):
    post_id = message.get_args()
    if post_id.isdigit():
        await db.delete_post(int(post_id))
        await message.answer(f"Пост {post_id} удален.")
    else:
        await message.answer("Пожалуйста, укажите корректный ID поста.")

@dp.message_handler(commands=['post_details'], user_id=ADMINS)
async def post_details(message: types.Message):
    post_id = message.get_args()
    post = await db.get_post_by_id(int(post_id))
    if post:
        await message.answer(f"Детали поста:\nID: {post[0]}\nГород: {post[1]}\nУлица: {post[2]}\nПлощадь: {post[3]} кв.м.")
    else:
        await message.answer("Пост с таким ID не найден.")

@dp.message_handler(commands=['view_posts'])
async def view_posts(message: types.Message):
    posts = await db.get_posts()  # Здесь можно добавить фильтрацию по статусу одобрения
    if posts:
        response = "\n".join([f"ID: {post[0]} Город: {post[1]}, Улица: {post[2]}, {post[3]} кв. м." for post in posts])
        await message.answer(response)
    else:
        await message.answer("В данный момент доступных постов нет.")