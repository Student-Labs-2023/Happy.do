from aiogram.dispatcher.filters.state import State, StatesGroup


class UserState(StatesGroup):
    limit_is_over = State()
    personal_smile_add = State()
    personal_smile_remove = State()
