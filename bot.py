import logging
import os
from datetime import date
import calendar
from aiogram.types.message import ContentType
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
    "😊", "😀", "🤪", "😍", "😅",
    "😆", "😉", "😌", "😎", "😏",
    "🤔", "😒", "😔", "😕", "😖",
    "🤢", "😟", "😠", "😡", "😢",
    "😣", "😥", "😪", "😫", "😴"]

"""списки для кнопок"""
buttons_menu = ["Статистика", "Выбрать смайлик", "Премиум"]
admin_menu = ["Кол-во новых пользователей за неделю", "Общее кол-во пользовтелей", "Статистика за день",
              "Статистика за неделю", "Статистика за месяц", "Выйти"]
premium_list = ["1 месяц", "6 месяцев", "1 год"]

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
        await message.answer("Ваша статистика за всё время")
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
    date_day = str(date.today())
    await database.addOrChangeSmile(callback_query.from_user.id, date_day, query.data)


@dp.message_handler(commands=['admin'])
async def admin(message: types.Message):
    if message.from_user.id == config.ADMIN_ID:
        await message.answer('Выполнен вход в админ-панель', reply_markup=show_button(admin_menu))


@dp.message_handler(text=["Кол-во новых пользователей за неделю"])
async def stat_new_week(message: types.Message):
    if message.from_user.id == config.ADMIN_ID:
        await message.answer(f'Кол-во новых пользователей за неделю: {await database.getCountNewUsers()}',
                             reply_markup=show_button(admin_menu))


@dp.message_handler(text=["Общее кол-во пользовтелей"])
async def stat_all(message: types.Message):
    if message.from_user.id == config.ADMIN_ID:
        await message.answer(f'Общее кол-во пользовтелей: {await database.getCountAllUsers()}',
                             reply_markup=show_button(admin_menu))


@dp.message_handler(text=["Статистика за день"])
async def stat_day(message: types.Message):
    if message.from_user.id == config.ADMIN_ID:
        info = await database.getStatAdmin(1)
        await message.answer(f'Статистика за день: {info}', reply_markup=show_button(admin_menu))


@dp.message_handler(text=["Статистика за неделю"])
async def stat_week(message: types.Message):
    if message.from_user.id == config.ADMIN_ID:
        info = await database.getStatAdmin(7)
        await message.answer(f'Статистика за неделю: \n{" ".join(info)}', reply_markup=show_button(admin_menu))


@dp.message_handler(text=["Статистика за месяц"])
async def stat_month(message: types.Message):
    if message.from_user.id == config.ADMIN_ID:
        info = await database.getStatAdmin(30)
        await message.answer(f'Статистика за месяц: {info}', reply_markup=show_button(admin_menu))


@dp.message_handler(text=["Выйти"])
async def admin_exit(message: types.Message):
    if message.from_user.id == config.ADMIN_ID:
        await message.reply('Выход из админ-панели', reply_markup=show_button(buttons_menu))


@dp.message_handler(text=["Премиум"])
async def premium(message: types.Message):
    await message.reply('Выбери на какой срок подкоючить премиум', reply_markup=show_button(premium_list))



async def send_invoice(chat_id, time, price):
    PRICE = types.LabeledPrice(label=f"Подписка на {time}", amount=price * 100)

    await bot.send_invoice(
        chat_id=chat_id,
        title='Premium Happy.do',
        description=f'Активация подписки на {time}',
        provider_token=config.PAYMENTS_TOKEN.get_secret_value(),
        currency="rub",
        photo_url="https://info.sibnet.ru/ni/629/629577w_1669101196.jpg",
        photo_width=416,
        photo_height=234,
        photo_size=416,
        is_flexible=False,
        prices=[PRICE],
        start_parameter="",
        payload="test-invoice-payload"
    )


@dp.message_handler(text=['1 месяц'])
async def buy(message: types.Message, time='1 месяц', price=100):
    await send_invoice(message.chat.id, time, price)


@dp.message_handler(text=['6 месяцев'])
async def buy(message: types.Message, time='6 месяцев', price=200):
    await send_invoice(message.chat.id, time, price)


@dp.message_handler(text=['1 год'])
async def buy(message: types.Message, time='1 год', price=500):
    await send_invoice(message.chat.id, time, price)


@dp.pre_checkout_query_handler(lambda query: True)
async def pre_checkout_query(pre_checkout_q: types.PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_q.id, ok=True)


@dp.message_handler(content_types=ContentType.SUCCESSFUL_PAYMENT)
async def successful_payment(message: types.Message):
    print("SUCCESSFUL PAYMENT")
    payment_info = message.successful_payment.to_python()
    for k, v in payment_info.items():
        print(f"{k}={v}")

    await bot.send_message(message.chat.id, f"Платеж на сумму {message.successful_payment.total_amount } {message.successful_payment.currency} Прошел успешно")

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    start_webhook(
        dispatcher=dp,
        webhook_path=WEBHOOK_PATH,
        skip_updates=False,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
        host=WEBAPP_HOST,
        port=WEBAPP_PORT,
    )
    dp.register_message_handler(show_emoji)
    dp.register_callback_query_handler(button)
