import logging
import os
from datetime import date

import calendar
from aiogram.types.message import ContentType
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import Dispatcher, FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from aiogram.utils.executor import start_webhook
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from aiogram import Bot, types

from tgbot.utiles.Statistics import statistics
from tgbot.utiles import database
from config import config

bot = Bot(token=config.BOT_TOKEN.get_secret_value())
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

WEBHOOK_HOST = config.WEBHOOK_HOST
WEBHOOK_PATH = f'/webhook/{config.BOT_TOKEN.get_secret_value()}'
WEBHOOK_URL = f'{WEBHOOK_HOST}{WEBHOOK_PATH}'

WEBAPP_HOST = config.WEBAPP_HOST
WEBAPP_PORT = config.WEBAPP_PORT


async def on_startup(dispatcher):
    await bot.set_webhook(WEBHOOK_URL, drop_pending_updates=True)


async def on_shutdown(dispatcher):
    await bot.delete_webhook()


class UserState(StatesGroup):
    limit_is_over = State()


smileys = [
    "😊", "😀", "🤪", "😍", "😅",
    "😆", "😉", "😌", "😎", "😏",
    "🤔", "😒", "😔", "😕", "😖",
    "🤢", "😟", "😠", "😡", "😢",
    "😣", "😥", "😪", "😫", "😴"]

"""списки для кнопок"""
buttons_menu = ["Статистика", "Выбрать смайлик", "Премиум"]

buttons_stat = ["День", "Неделя", "Месяц", "Все время", "Вернуться"]
admin_menu = ["Кол-во новых пользователей за неделю", "Общее кол-во пользователей", "Статистика за день",
              "Статистика за неделю", "Статистика за месяц", "Выйти"]

premium_list_default = ["1 месяц", "6 месяцев", "1 год", "Вернуться"]
premium_list_state = ["1 месяц", "6 месяцев", "1 год"]


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


@dp.message_handler(text=["Премиум"])
async def premium(message: types.Message):
    await message.reply('Выбери на какой срок подключить премиум', reply_markup=show_button(premium_list_default))


@dp.message_handler(text=['1 месяц', '6 месяцев', '1 год'])
@dp.message_handler(state=UserState.limit_is_over)
async def buy(message: types.Message, time='1 год', price=500):
    if message.text == '1 месяц':
        await send_invoice(message.chat.id, '1 месяц', price=100)
    elif message.text == '6 месяцев':
        await send_invoice(message.chat.id, '6 месяцев', price=200)
    elif message.text == '1 год':
        await send_invoice(message.chat.id, '1 год', price=500)

        
@dp.message_handler(state=UserState.limit_is_over)
async def buy_premium(message: types.Message):
    await message.answer('Чтобы продолжить купи подписку')


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer(f'Привет, {message.from_user.first_name}!')
    user_exists = await database.checkUser(message.from_user.id)
    if not user_exists:
        await database.createUser(message.from_user.id, message.from_user.username)
    await message.answer('Выбери что тебя интересует', reply_markup=show_button(buttons_menu))


@dp.message_handler(text=["Вернуться"])
async def statisticUserBack(message: types.Message):
    await message.answer('Выбери что тебя интересует', reply_markup=show_button(buttons_menu))


@dp.message_handler(text=["Статистика"])
async def statisticUser(message: types.Message):
    user_id = message.from_user.id  # ID чата
    await message.answer('За какой период ты хочешь получить статистику?', reply_markup=show_button(buttons_stat))


@dp.message_handler(text=["День"])
async def statisticUserDay(message: types.Message):
    user_id = message.from_user.id  # ID чата
    userSmiles = database.getSmileInfo(user_id, str(date.today()))
    new_emoji_list = add_checkmark(smileys, userSmiles)
    pathToPicture = await statistics.analiticData(user_id, "day", str(date.today()))  # путь к картинке со статой
    if pathToPicture != "absent":
        await message.answer("Ваша статистика за день")
        photo = InputFile(pathToPicture)
        await bot.send_photo(chat_id=message.chat.id, photo=photo, reply_markup=show_inline_button(new_emoji_list))
        os.remove(pathToPicture)  # удаляем файл с картинкой
    else:
        await message.answer("Недостаточно данных. Возможно вы еще не ввели смайлики за этот период.")


@dp.message_handler(text=["Неделя"])
async def statisticUserWeek(message: types.Message):
    user_id = message.from_user.id  # ID чата
    pathToPicture = await statistics.analiticData(user_id, "week")  # путь к картинке со статой
    if pathToPicture != "absent":
        await message.answer("Ваша статистика за неделю")
        photo = InputFile(pathToPicture)
        await bot.send_photo(chat_id=message.chat.id, photo=photo)
        os.remove(pathToPicture)  # удаляем файл с картинкой
    else:
        await message.answer("Недостаточно данных. Возможно вы еще не ввели смайлики за этот период.")


@dp.message_handler(text=["Месяц"])
async def statisticUserMonth(message: types.Message):
    user_id = message.from_user.id  # ID чата
    pathToPicture = await statistics.analiticData(user_id, "month")  # путь к картинке со статой
    if pathToPicture != "absent":
        await message.answer("Ваша статистика за месяц")
        photo = InputFile(pathToPicture)
        await bot.send_photo(chat_id=message.chat.id, photo=photo)
        os.remove(pathToPicture)  # удаляем файл с картинкой
    else:
        await message.answer("Недостаточно данных. Возможно вы еще не ввели смайлики за этот период.")


@dp.message_handler(text=["Все время"])
async def statisticUserAll(message: types.Message):
    user_id = message.from_user.id  # ID чата
    pathToPicture = await statistics.analiticData(user_id, "all")  # путь к картинке со статой
    if pathToPicture != "absent":
        await message.answer("Ваша статистика за все время")
        photo = InputFile(pathToPicture)
        await bot.send_photo(chat_id=message.chat.id, photo=photo)
        os.remove(pathToPicture)  # удаляем файл с картинкой
    else:
        await message.answer("Недостаточно данных. Возможно вы еще не ввели смайлики за этот период.")


def show_button(list_menu):
    """Принимает список и превращает его в кнопки"""
    """создает кнопки для меню"""
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(*list_menu)
    return keyboard


# def show_inline_button(list_emoji):
#     """Принимает список и превращает его в инлайн кнопки"""
#     keyboard = InlineKeyboardMarkup(row_width=5)
#     buttons = [InlineKeyboardButton(smiley, callback_data=smiley) for smiley in list_emoji]
#     keyboard.add(*buttons)
#     return keyboard


def show_inline_button(emoji_list, selected_emojis=[]):
    buttons = []
    for emoji in emoji_list:
        if emoji in selected_emojis:
            button_text = emoji + "✅"
        else:
            button_text = emoji
        buttons.append(InlineKeyboardButton(button_text, callback_data=emoji))
    return InlineKeyboardMarkup(row_width=5).add(*buttons)


def add_checkmark(lst, variable):
    return [elem + "✅" if elem == variable else elem for elem in lst]


@dp.message_handler(text=["Выбрать смайлик"])
async def show_emoji(message: types.Message):
    await message.reply('Выберите смайлик:', reply_markup=show_inline_button(smileys))


# @dp.callback_query_handler()
# async def button(callback_query: types.CallbackQuery, state: FSMContext):
#     query = callback_query
#     await query.answer()
#     new_emoji_list = add_checkmark(smileys, query.data)
#     await bot.answer_callback_query(callback_query.id)
#     await query.message.edit_text('Выбранный смайлик ✅', reply_markup=show_inline_button(new_emoji_list))
#     await database.addEmojiUsed(callback_query.from_user.id)
#     date_day = str(date.today())
#     await database.addOrChangeSmile(callback_query.from_user.id, date_day, query.data)
#
#     limit_end = await database.emojiLimitExpired(callback_query.from_user.id)
#     if limit_end:
#         await state.set_state(UserState.limit_is_over.state)
#         await callback_query.message.answer('Чтобы продолжить купи подписку')


@dp.callback_query_handler()
async def button(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id

    async with state.proxy() as data:

        if "selected_emojis" not in data:
            data["selected_emojis"] = []

        selected_emojis = data["selected_emojis"]

        selected_emoji = callback_query.data

        # Проверяем, есть ли выбранный смайлик уже в списке выбранных
        if selected_emoji not in selected_emojis:
            # Если смайлика еще нет в списке выбранных, добавляем его
            selected_emojis.append(selected_emoji)
            await callback_query.answer("Вы выбрали смайлик ✅")
        else:
            # Если смайлик уже есть в списке выбранных, удаляем его, чтобы пользователь мог снова выбрать
            selected_emojis.remove(selected_emoji)
            await callback_query.answer("Смайлик снят ❌")

        data["selected_emojis"] = selected_emojis

        print(selected_emojis)
        await database.addOrChangeSmile(callback_query.from_user.id, str(date.today()), selected_emojis)

        await callback_query.message.edit_text(
            "Выбранные смайлики:\n" + "".join(selected_emojis) if selected_emojis else "Выбранных смайликов пока нет.",
            reply_markup=show_inline_button(smileys, selected_emojis)
        )   


async def set_state(message: types.Message, state: FSMContext):
    await state.set_state(UserState.limit_is_over.state)
    await message.answer(
        'Вы использовали свой лимит в 100 смайликов, чтобы продолжить вам необходимо'
        'приобрести premium подписку, выберете подписки', reply_markup=show_button(premium_list_state))



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
        await message.answer(f'Статистика за день: \n{info}', reply_markup=show_button(admin_menu))


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


@dp.pre_checkout_query_handler(lambda query: True)
async def pre_checkout_query(pre_checkout_q: types.PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_q.id, ok=True)


@dp.message_handler(content_types=ContentType.SUCCESSFUL_PAYMENT)
async def successful_payment(message: types.Message, state: FSMContext):
    print("SUCCESSFUL PAYMENT")
    await state.finish()
    payment_info = message.successful_payment.to_python()
    for k, v in payment_info.items():
        print(f"{k}={v}")


    await bot.send_message(message.chat.id,
                           f"Платеж на сумму {message.successful_payment.total_amount // 100}."
                           f"{message.successful_payment.currency} прошел успешно",
                           reply_markup=show_button(buttons_menu))


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
