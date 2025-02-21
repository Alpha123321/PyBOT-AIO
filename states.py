from aiogram.dispatcher.filters.state import StatesGroup, State

class PostForm(StatesGroup):
    waiting_for_city = State()
    waiting_for_street = State()
    waiting_for_square_meters = State()