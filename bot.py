import logging
import os
from datetime import date
import calendar

from aiogram.dispatcher import Dispatcher
from aiogram.utils.executor import start_webhook
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from aiogram import Bot, types

from tgbot.utiles.Statistics import statistics
from tgbot.utiles import database
from config import config

bot = Bot(token=config.BOT_TOKEN.get_secret_value())
dp = Dispatcher(bot)

WEBHOOK_HOST = config.WEBHOOK_HOST
WEBHOOK_PATH = f'/webhook/{config.BOT_TOKEN.get_secret_value()}'
WEBHOOK_URL = f'{WEBHOOK_HOST}{WEBHOOK_PATH}'

WEBAPP_HOST = config.WEBAPP_HOST
WEBAPP_PORT = config.WEBAPP_PORT


async def on_startup(dispatcher):
    await bot.set_webhook(WEBHOOK_URL, drop_pending_updates=True)


async def on_shutdown(dispatcher):
    await bot.delete_webhook()


smileys = [
    ["😊", "😀", "🤪", "😍", "😅",
     "😆", "😉", "😌", "😎", "😏",
     "🤔", "😒", "😔", "😕", "😖",
     "🤢", "😟", "😠", "😡", "😢",
     "😣", "😥", "😪", "😫", "😴"]
]
"""списки для кнопок"""
buttons_menu = ["Статистика", "Выбрать смайлик"]


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer(f'Привет, {message.from_user.first_name}!')
    user_exists = await database.checkUser(str(message.from_user.id))
    if not user_exists:
        await database.createUser(message.from_user.id, message.from_user.username)
    await message.answer('Выбери что тебя интересует', reply_markup=show_button(buttons_menu))


@dp.message_handler(text=["Статистика"])
async def statisticUser(message: types.Message):
    user_id = message.from_user.id  # ID чата
    pathToPicture = await statistics.analiticData(user_id)  # путь к картинке со статой
    if pathToPicture != "absent":
        await message.answer("Ваша статистика за неделю")
        photo = InputFile(pathToPicture)
        await bot.send_photo(chat_id=message.chat.id, photo=photo)
        os.remove(pathToPicture)  # удаляем файл с картинкой
    else:
        await message.answer("Статистика отсутствует. Вы еще ни разу не вводили смайлики.")


def show_button(list_menu):
    """Принимает список и превращает его в кнопки"""
    """создает кнопки для меню"""
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(*list_menu)
    return keyboard


def show_inline_button(list_emoji):
    """Принимает список и превращает его в инлайн кнопки кнопки"""
    "создает инлайн кнопки для показа смайликов"
    keyboard = InlineKeyboardMarkup(row_width=5)
    buttons = [InlineKeyboardButton(smiley, callback_data=smiley) for smiley in list_emoji]
    keyboard.add(*buttons)
    return keyboard


def add_checkmark(lst, variable):
    return [elem + "✅" if elem == variable else elem for elem in lst]


@dp.message_handler(text=["Выбрать смайлик"])
async def show_emoji(message: types.Message):
    await message.reply('Выберите смайлик:', reply_markup=show_inline_button(smileys))


@dp.callback_query_handler()
async def button(callback_query: types.CallbackQuery):
    query = callback_query
    await query.answer()
    new_emoji_list = add_checkmark(smileys, query.data)
    await bot.answer_callback_query(callback_query.id)
    await query.message.edit_text('Выбранный смайлик ✅', reply_markup=show_inline_button(new_emoji_list))
    date_day = date.today()
    date_name = calendar.day_name[date_day.weekday()]
    await database.addOrChangeSmile(callback_query.from_user.id, date_name, '' if '✅' in query.data else query.data)



if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    start_webhook(
        dispatcher=dp,
        webhook_path=WEBHOOK_PATH,
        skip_updates=True,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
        host=WEBAPP_HOST,
        port=WEBAPP_PORT,
    )
    dp.register_message_handler(show_emoji)
    dp.register_callback_query_handler(button)
