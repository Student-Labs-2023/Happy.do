import logging
import os
from datetime import date, datetime, timedelta
import emoji

from aiogram.types.message import ContentType
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import Dispatcher, FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from aiogram.utils.executor import start_webhook
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from aiogram import Bot, types

from tgbot.utiles.Statistics import statistics, pictureNoData
from tgbot.utiles import database, chatGPT
from config import config
from tgbot.utiles.supportFunctions import converting_dates_to_days

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
    personal_smile_add = State()
    personal_smile_remove = State()


smileys = [
    "😊", "😀", "🤪", "😍", "😅",
    "😆", "😉", "😌", "😎", "😏",
    "🤔", "😒", "😔", "😕", "😖",
    "🤢", "😟", "😠", "😡", "😢",
    "😣", "😥", "😪", "😫", "😴"]

"""списки для кнопок"""
buttons_menu = ["Статистика", "Выбрать смайлик", "Добавить смайлик", "Сгенерировать портрет", "Премиум"]

buttons_stat = ["День", "Неделя", "Месяц", "Все время", "Вернуться"]
admin_menu = ["Кол-во новых пользователей за неделю", "Общее кол-во пользователей", "Статистика за день",
              "Статистика за неделю", "Статистика за месяц", "Выйти"]
buttons_addSmileToMenu = ["Добавить", "Удалить", "Вернуться"]

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
    if await database.checkPremiumUser(message.from_user.id):
        await message.reply(await database.infoPremiumUser(message.from_user.id),
                            reply_markup=show_button(["Вернуться"]))
    else:
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
    await message.answer(f'Привет, {message.from_user.first_name}! Happy.do – это бот, который помогает пользователям '
                         f'отслеживать свое ежедневное состояние и деятельность с помощью смайликов. Это уникальный '
                         f'инструмент рефлексии, который помогает улучшить осознанность и поддерживать эмоциональное '
                         f'здоровье.')
    user_exists = await database.checkUser(message.from_user.id)
    if not user_exists:
        await database.createUser(message.from_user.id, message.from_user.username)
    await message.answer('Выбери что тебя интересует', reply_markup=show_button(buttons_menu))


@dp.message_handler(text=["Вернуться"])
async def statisticUserBack(message: types.Message):
    await message.answer('Выбери что тебя интересует', reply_markup=show_button(buttons_menu))


# -----------------------------------------------------------------------------------------------------------------------
"""Система отправки статистики"""
#-----------------------------------------------------------------------------------------------------------------------


@dp.message_handler(text=["Статистика"])
async def statisticUser(message: types.Message):
    user_id = message.from_user.id  # ID чата
    await message.answer('За какой период ты хочешь получить статистику?', reply_markup=show_button(buttons_stat))


@dp.message_handler(text=["День"])
async def statisticUserDay(message: types.Message, state: FSMContext, day=str(date.today())):
    user_id = message.from_user.id  # ID чата
    pathToPicture = await statistics.analiticData(user_id, "day", day)  # путь к картинке со статой
    emoji_list = smileys + await database.getPersonalSmiles(user_id)

    # await message.answer("Ваша статистика за день")
    if pathToPicture != "absent":
        photo = InputFile(pathToPicture)
        userSmiles = await database.getSmileInfo(user_id, day)
        sent_message = await message.answer_photo(photo=photo,
                                                  reply_markup=show_fake_inline_button(emoji_list, userSmiles))
        async with state.proxy() as data:
            if "message_id" in data:
                try:
                    await bot.delete_message(chat_id=user_id, message_id=data["message_id"])
                except Exception as e:
                    print(f"Не удалось удалить сообщение с ID {data['message_id']}: {e}")
            data['message_id'] = sent_message.message_id
    else:
        pathToPicture = pictureNoData.createPictureNoData(user_id, day)
        photo = InputFile(pathToPicture)
        sent_message = await message.answer_photo(photo=photo,
                                                  reply_markup=show_fake_inline_button(emoji_list))
        async with state.proxy() as data:
            if "message_id" in data:
                try:
                    await bot.delete_message(chat_id=user_id, message_id=data["message_id"])
                except Exception as e:
                    print(f"Не удалось удалить сообщение с ID {data['message_id']}: {e}")
            data['message_id'] = sent_message.message_id

    os.remove(pathToPicture)  # удаляем файл с картинкой


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


def show_fake_inline_button(emoji_list, selected_emojis=[], date_offset=0):
    """ Создает инлайн-кнопки, которые не влияют на базу данных,
        для визуального отображения выбора в статистике за день.

        Также, добавляет кнопки перелистывания даты в виде стрелок. """
    buttons = []
    keyboard = InlineKeyboardMarkup(row_width=5)

    for emoji in emoji_list:
        if emoji in selected_emojis:
            button_text = emoji + "✅"
        else:
            button_text = emoji
        buttons.append(InlineKeyboardButton(button_text, callback_data="fake_buttons"))

    button1 = InlineKeyboardButton("⬅️", callback_data=f"fake_left_arrow_{date_offset}")
    button2 = InlineKeyboardButton("➡️", callback_data=f"fake_right_arrow_{date_offset}")

    keyboard.add(*buttons)
    keyboard.row(button1, button2)

    return keyboard


@dp.callback_query_handler(text="fake_buttons")
async def fake_inline_button_functions(callback_query: types.CallbackQuery):
    """Функционал для фейк кнопок со смайликами.
       Отправляет пользователю сообщение о том, что здесь выбор менять нельзя"""
    await callback_query.answer("Здесь смайлы изменять нельзя!")


@dp.callback_query_handler(lambda callback_query: callback_query.data.startswith(
    "fake_left_arrow_"))  # проверка на наличие текста "fake_left_arrow_" в колбеке
async def fake_left_arrow(callback_query: types.CallbackQuery, state: FSMContext):
    """
    Функционал кнопки перелистывания даты влево.
    """
    # Извлекаем смещение даты из callback_query.data
    date_offset = int(callback_query.data.split("_")[-1])
    # Уменьшаем смещение на 1 день
    new_date_offset = date_offset - 1
    # Обновляем сообщение с новым смещением
    await update_message_with_offset(callback_query.message, state, new_date_offset, callback_query.from_user.id)


@dp.callback_query_handler(lambda callback_query: callback_query.data.startswith("fake_right_arrow_"))
async def fake_right_arrow(callback_query: types.CallbackQuery, state: FSMContext):
    """
    Функционал кнопки перелистывания даты вправо.
    """
    # Извлекаем смещение даты из callback_query.data
    date_offset = int(callback_query.data.split("_")[-1])
    # Увеличиваем смещение на 1 день
    new_date_offset = date_offset + 1
    # Обновляем сообщение с новым смещением
    await update_message_with_offset(callback_query.message, state, new_date_offset, callback_query.from_user.id)


async def update_message_with_offset(message: types.Message, state: FSMContext, date_offset: int, user_id: int):
    """
    Функция для изменения сообщения статистики.
    """
    # получаем из стейта message_id
    async with state.proxy() as data:
        msg_id = data['message_id']

    smile_list = smileys + await database.getPersonalSmiles(user_id)

    async def pastPicture():
        """
        Функция для отправки картинки с отсутствием данных
        """
        pathToPicture = pictureNoData.createPictureNoData(user_id, new_date)

        with open(pathToPicture, 'rb') as file:
            photo = types.InputMediaPhoto(file)

            await bot.edit_message_media(
                chat_id=user_id,
                message_id=msg_id,
                media=photo,
                reply_markup=show_fake_inline_button(smile_list, date_offset=date_offset)
            )
        os.remove(pathToPicture)

    # Получаем текущую дату и применяем смещение
    new_date = str(date.today() + timedelta(days=date_offset))

    """ Проверяем на наличие данных по указанному дню в базе 
    и при положительном ответе изменяем сообщение с добавлением новой статистики """
    try:
        userSmiles = await database.getSmileInfo(user_id, new_date)
        pathToPicture = await statistics.analiticData(user_id, "day", new_date)  # путь к картинке со статой
        if pathToPicture != "absent":

            with open(pathToPicture, 'rb') as file:
                photo = types.InputMediaPhoto(file)

                await bot.edit_message_media(
                    chat_id=user_id,
                    message_id=msg_id,
                    media=photo,
                    reply_markup=show_fake_inline_button(smile_list, userSmiles, date_offset)
                )
            os.remove(pathToPicture)  # удаляем файл с картинкой
        else:
            await pastPicture()
    except KeyError:
        await pastPicture()

        
#-----------------------------------------------------------------------------------------------------------------------
"""Добавление смайлика к таблице выбора"""
#-----------------------------------------------------------------------------------------------------------------------


@dp.message_handler(text=["Добавить смайлик"])
async def addSmileToMenu(message: types.Message):
    await message.answer("Выберите действие", reply_markup=show_button(buttons_addSmileToMenu))


@dp.message_handler(text=["Добавить"])
async def addSmile(message: types.Message):
    personal_smiles = await database.getPersonalSmiles(message.from_user.id)
    if len(personal_smiles) < 10:
        await message.answer("Отправьте смайлик, который вы хотите добавить. Премиум смайлики добавлять нельзя.",
                             reply_markup=show_button(["Вернуться"]))
        await UserState.personal_smile_add.set()
    else:
        await message.answer("Вы уже добавили максимальное количество смайликов - 10. "
                             "Вы можете освободить место, удалив один из добавленных смайликов.")


@dp.message_handler(state=UserState.personal_smile_add)
async def addPersonalSmile(message: types.Message, state: FSMContext):
    personal_smile = ""
    user_id = message.from_user.id
    smile_list = smileys + await database.getPersonalSmiles(user_id)

    if message.sticker:
        personal_smile = message.sticker.emoji
    elif message.text:
        personal_smile = message.text

    if len(personal_smile) == 1 and bool(emoji.emoji_count(personal_smile)):
        if personal_smile in smile_list:
            await message.answer(f"{personal_smile} - такой смайлик уже есть. Выберите другой.")
        else:
            await message.answer(f"{personal_smile} - ваш смайл.")
            await database.addPersonalSmiles(user_id, personal_smile)
            await state.finish()
            await message.answer('Выбери что тебя интересует', reply_markup=show_button(buttons_menu))
    elif personal_smile == 'Вернуться':
        await state.finish()
        await message.answer('Выбери что тебя интересует', reply_markup=show_button(buttons_menu))
    else:
        await message.answer("Неправильный ввод! Отправьте смайлик.\n"
                             "Если вы не хотите отправлять смайл, то нажмите 'Вернуться'")


@dp.message_handler(text=["Удалить"])
async def deleteSmile(message: types.Message):
    personal_smiles = await database.getPersonalSmiles(message.from_user.id)
    if len(personal_smiles) > 0:
        await message.answer("Отправьте смайлик, который вы хотите удалить.")
        await UserState.personal_smile_remove.set()
    else:
        await message.answer("Вы не добавили ни одного смайлика."
                             "Можно удалить только добавленные смайлики.")


@dp.message_handler(state=UserState.personal_smile_remove)
async def deletePersonalSmile(message: types.Message, state: FSMContext):
    personal_smile = ""
    user_id = message.from_user.id
    smile_list = await database.getPersonalSmiles(user_id)

    if message.sticker:
        personal_smile = message.sticker.emoji
    elif message.text:
        personal_smile = message.text

    if len(personal_smile) == 1 and bool(emoji.emoji_count(personal_smile)):
        if personal_smile in smileys:
            await message.answer(f"{personal_smile} - этот смайлик находится в стандартном меню выбора, "
                                 f"его нельзя удалять. Выберите другой.")
        elif not personal_smile in smile_list:
            await message.answer(
                f"{personal_smile} - этого смайлика нет в добавленных вами смайликах. Выберите другой.")
        else:
            await message.answer(f"{personal_smile} - ваш смайл.")
            await database.removePersonalSmile(user_id, personal_smile)
            await state.finish()
            await message.answer('Выбери что тебя интересует', reply_markup=show_button(buttons_menu))
    elif personal_smile == 'Вернуться':
        await state.finish()
        await message.answer('Выбери что тебя интересует', reply_markup=show_button(buttons_menu))
    else:
        await message.answer("Неправильный ввод! Отправьте смайлик.\n"
                             "Если вы не хотите отправлять смайл, то выберите: 'Вернуться'")


#-----------------------------------------------------------------------------------------------------------------------
"""Генерация портрета с помощью chatGPT"""
#-----------------------------------------------------------------------------------------------------------------------


@dp.message_handler(text=["Сгенерировать портрет"])
async def generationPortrait(message: types.Message):
    await message.answer("Выбери за какой период ты хочешь сгенерировать психологический портрет.",
                         reply_markup=show_button(["За день", "За неделю", "Вернуться"]))


@dp.message_handler(text=["За день"])
async def generationPortraitDay(message: types.Message):
    """
    Отправляет пользователю сгенерированный психологический портрет chatGPT за день. Если пользователь не вводил смайлики
    сегодня или вызывал команду генерации портрета более 2 раз, то он не генерируется.
    """
    user_id = message.from_user.id

    if await database.getUsedGPT(user_id) < 2:
        try:
            smiles = await database.getSmileInfo(user_id, str(date.today()))
            smiles = ", ".join(smiles)
            await message.answer("Портрет генерируется. Дождитесь завершения.",
                                 reply_markup=types.ReplyKeyboardRemove())
            portrait = await database.getExistingPortrait(smiles, "day")
            if portrait == "NotExist":
                portrait = await chatGPT.create_psychological_portrait_day(", ".join(smiles))
                await database.addPortrait(smiles, portrait, "day")
            await message.answer(portrait, reply_markup=show_button(buttons_menu))
            await database.addUsedGPT(user_id)
        except KeyError:
            await message.answer("Вы не выбрали ни одного смайлика за сегодня.",
                                 reply_markup=show_button(buttons_menu))
    else:
        await message.answer("Превышен лимит использований команды на сегодня. Попробуйте сгенерировать портрет завтра")


@dp.message_handler(text=["За неделю"])
async def generationPortraitWeek(message: types.Message):
    """
    Отправляет пользователю сгенерированный психологический портрет chatGPT за неделю. Если пользователь не вводил смайлики
    хотя бы 7 дней или вызывал эту команду более 2 раз, то портрет не генерируется.
    """
    user_id = message.from_user.id

    if await database.getUsedGPT(user_id) < 2:

        smilesDict = await database.getSmileInfo(user_id, "all")

        if len(smilesDict) < 7:
            await message.answer("Слишком мало информации. Для получения портрета необходимо "
                                 "ставить смайлики в течении 7 дней", reply_markup=show_button(buttons_menu))
        else:
            await message.answer("Портрет генерируется. Дождитесь завершения.", reply_markup=show_button([]))
            smilesDict = converting_dates_to_days(dict(list(smilesDict.items())[-7:]))
            smiles = '\n'.join('{}: {}'.format(key, val) for key, val in smilesDict.items())  # Словарь в строку

            portrait = await database.getExistingPortrait(smiles, "week")
            if portrait == "NotExist":
                portrait = await chatGPT.create_psychological_portrait_week(", ".join(smiles))
                await database.addPortrait(smiles, portrait, "week")
            await message.answer(portrait, reply_markup=show_button(buttons_menu))
            await database.addUsedGPT(user_id)
    else:
        await message.answer("Превышен лимит использований команды на сегодня. Попробуйте сгенерировать портрет завтра")


# -----------------------------------------------------------------------------------------------------------------------
"""Остальные"""
# -----------------------------------------------------------------------------------------------------------------------


def show_button(list_menu):
    """Принимает список и превращает его в кнопки"""
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(*list_menu)
    return keyboard


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
    emoji_list = smileys + await database.getPersonalSmiles(message.from_user.id)
    await message.reply('Выберите смайлик:', reply_markup=show_inline_button(emoji_list))


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

        emoji_list = smileys + await database.getPersonalSmiles(user_id)
        await callback_query.message.edit_text(
            "Выбранные смайлики:\n" + "".join(selected_emojis) if selected_emojis else "Выбранных смайликов пока нет.",
            reply_markup=show_inline_button(emoji_list, selected_emojis)
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


@dp.message_handler(text=["Общее кол-во пользователей"])
async def stat_all(message: types.Message):
    if message.from_user.id == config.ADMIN_ID:
        await message.answer(f'Общее кол-во пользователей: {await database.getCountAllUsers()}',
                             reply_markup=show_button(admin_menu))


@dp.message_handler(text=["Статистика за день"])
async def stat_day(message: types.Message):
    if message.from_user.id == config.ADMIN_ID:
        info = await database.getStatAdmin(1)
        await message.answer(f'Статистика за день: \n{" ".join(info)}', reply_markup=show_button(admin_menu))


@dp.message_handler(text=["Статистика за неделю"])
async def stat_week(message: types.Message):
    if message.from_user.id == config.ADMIN_ID:
        info = await database.getStatAdmin(7)
        await message.answer(f'Статистика за неделю: \n{" ".join(info)}', reply_markup=show_button(admin_menu))


@dp.message_handler(text=["Статистика за месяц"])
async def stat_month(message: types.Message):
    if message.from_user.id == config.ADMIN_ID:
        info = await database.getStatAdmin(30)
        await message.answer(f'Статистика за месяц: \n{" ".join(info)}', reply_markup=show_button(admin_menu))


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

    await message.answer(
        "Платеж на сумму {:.2f} {} прошел успешно".format(float(message.successful_payment.total_amount) / 100,
                                                          message.successful_payment.currency),
        reply_markup=show_button(buttons_menu))
    await message.answer(await database.infoPremiumUser(message.from_user.id))

    current_date = datetime.today()

    if message.successful_payment.total_amount / 100 == 100:
        data_end = current_date + timedelta(days=31)
    elif message.successful_payment.total_amount / 100 == 200:
        data_end = current_date + timedelta(days=182)
    else:
        data_end = current_date + timedelta(days=365)

    await database.premiumStatus(message.from_user.id, str(data_end.date()))


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
