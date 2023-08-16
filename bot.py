import logging
import os
from datetime import date, datetime, timedelta
from io import BytesIO

from aiogram.types.message import ContentType
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import Dispatcher, FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from aiogram.utils.exceptions import MessageToDeleteNotFound, MessageCantBeDeleted
from aiogram.utils.executor import start_webhook
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, InputFile, InputMediaPhoto
from aiogram import Bot, types

from tgbot.utiles.Statistics import statistics, pictureNoData
from tgbot.utiles import database, chatGPT
from config import config
from tgbot.utiles.supportFunctions import converting_dates_to_days, contains_emojis

bot = Bot(token=config.BOT_TOKEN.get_secret_value())
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

WEBHOOK_HOST = config.WEBHOOK_HOST
WEBHOOK_PATH = f'/webhook/{config.BOT_TOKEN.get_secret_value()}'
WEBHOOK_URL = f'{WEBHOOK_HOST}{WEBHOOK_PATH}'

WEBAPP_HOST = config.WEBAPP_HOST
WEBAPP_PORT = config.WEBAPP_PORT


class UserState(StatesGroup):
    limit_is_over = State()
    personal_smile_add = State()
    personal_smile_remove = State()


async def on_startup(dispatcher):
    await bot.set_webhook(WEBHOOK_URL, drop_pending_updates=True)
    await setUserStateFromDB()


async def on_shutdown(dispatcher):
    await bot.delete_webhook()


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
    prevInvoiceMsg = await database.getPrevInvoiceMsgID(chat_id)
    if prevInvoiceMsg is not None:
        await bot.delete_message(chat_id=chat_id, message_id=prevInvoiceMsg)

    PRICE = types.LabeledPrice(label=f"Подписка на {time}", amount=price * 100)
    Invoice = await bot.send_invoice(
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
    await database.updateInvoiceMsgID(chat_id, Invoice["message_id"])


@dp.message_handler(text=["Премиум"])
async def premium(message: types.Message, state: FSMContext):
    is_premium = await database.checkPremiumUser(message.from_user.id)
    premium_end = await database.checkPremiumIsEnd(message.from_user.id)
    if is_premium and not premium_end:
        await message.reply(await database.infoPremiumUser(message.from_user.id),
                            reply_markup=show_button(["Вернуться"]))
    elif is_premium and premium_end:
        await premiumIsEnd(user_id=message.from_user.id, state=state)
    else:
        await message.reply('Выбери на какой срок подключить премиум', reply_markup=show_button(premium_list_default))


@dp.message_handler(text=['1 месяц', '6 месяцев', '1 год'])
@dp.message_handler(state=UserState.limit_is_over)
async def buy(message: types.Message):
    if message.text == '1 месяц':
        await delMessage(message.chat.id, message.message_id)
        await send_invoice(message.chat.id, '1 месяц', price=100)
    elif message.text == '6 месяцев':
        await delMessage(message.chat.id, message.message_id)
        await send_invoice(message.chat.id, '6 месяцев', price=200)
    elif message.text == '1 год':
        await delMessage(message.chat.id, message.message_id)
        await send_invoice(message.chat.id, '1 год', price=500)


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer(f'Привет, {message.from_user.first_name}!\n<b>Happy.dо</b> – это бот, который помогает пользователям '
                         f'отслеживать свое ежедневное состояние и деятельность с помощью смайликов. Это уникальный '
                         f'инструмент рефлексии, который помогает улучшить осознанность и поддерживать эмоциональное '
                         f'здоровье.', parse_mode='HTML')
    user_exists = await database.checkUser(message.from_user.id)
    if not user_exists:
        await database.createUser(message.from_user.id, message.from_user.username)
    await message.answer('Выбери что тебя интересует', reply_markup=show_button(buttons_menu))


@dp.message_handler(text=["Вернуться"])
async def statisticUserBack(message: types.Message):
    await message.answer('Выбери что тебя интересует', reply_markup=show_button(buttons_menu))


# -----------------------------------------------------------------------------------------------------------------------
"""Система отправки статистики"""


# -----------------------------------------------------------------------------------------------------------------------


@dp.message_handler(text=["Статистика"])
async def statisticUser(message: types.Message, state: FSMContext):
    user_id = message.from_user.id  # ID чата
    premium_end = await database.checkPremiumIsEnd(user_id)
    if premium_end:
        await premiumIsEnd(user_id=user_id, state=state)
    else:
        await message.answer('За какой период ты хочешь получить статистику?', reply_markup=show_button(buttons_stat))


@dp.message_handler(text=["День"])
async def statisticUserDay(message: types.Message, state: FSMContext, day=str(date.today())):
    user_id = message.from_user.id  # ID чата
    premium_end = await database.checkPremiumIsEnd(user_id)
    if premium_end:
        await premiumIsEnd(user_id=user_id, state=state)
    else:
        pathToPicture = await statistics.analiticData(user_id, "day", day)  # путь к картинке со статой
        emoji_list = smileys + await database.getPersonalSmiles(user_id)
        picture = await statistics.analiticData(user_id, "day", day)  # путь к картинке со статой
        emoji_list = smileys + await database.getPersonalSmiles(user_id)

        if isinstance(picture, BytesIO):
            userSmiles = await database.getSmileInfo(user_id, day)
            sent_message = await message.answer_photo(photo=picture,
                                                      reply_markup=show_fake_inline_button(emoji_list, userSmiles))

            message_id = await database.getMessageId(user_id, "stat_day")
            if message_id is not None:
                try:
                    await bot.delete_message(chat_id=user_id, message_id=message_id)
                except Exception as e:
                    print(f"Не удалось удалить сообщение с ID {message_id}: {e}")
            message_id = sent_message.message_id
            await database.addMessageId(user_id, "stat_day", message_id)

        else:
            picture = pictureNoData.createPictureNoData(user_id, day)
            sent_message = await message.answer_photo(photo=picture,
                                                    reply_markup=show_fake_inline_button(emoji_list))

            message_id = await database.getMessageId(user_id, "stat_day")
            if message_id is not None:
                try:
                    await bot.delete_message(chat_id=user_id, message_id=message_id)
                except Exception as e:
                    print(f"Не удалось удалить сообщение с ID {message_id}: {e}")
            message_id = sent_message.message_id
            await database.addMessageId(user_id, "stat_day", message_id)

        picture = None  # Убираем ссылку на объект и освобождаем память



@dp.message_handler(text=["Неделя"])
async def statisticUserWeek(message: types.Message, state: FSMContext):
    user_id = message.from_user.id  # ID чата
    premium_end = await database.checkPremiumIsEnd(user_id)
    if premium_end:
        await premiumIsEnd(user_id=user_id, state=state)
    else:
        picture = await statistics.analiticData(user_id, "week")  # картинка со статой
        if isinstance(picture, BytesIO):
            # await message.answer("Ваша статистика за неделю")
            sent_message = await bot.send_photo(chat_id=message.chat.id, photo=picture)


            # message_id = await database.getMessageId(user_id, "stat_week")
            # if message_id is not None:
            #     try:
            #         await bot.delete_message(chat_id=user_id, message_id=message_id)
            #     except Exception as e:
            #         print(f"Не удалось удалить сообщение с ID {message_id}: {e}")
            # message_id = sent_message.message_id
            # await database.addMessageId(user_id, "stat_week", message_id)


            picture = None  # Убираем ссылку на объект и освобождаем память
        else:
            await message.answer("Недостаточно данных. Возможно вы еще не ввели смайлики за этот период.")


@dp.message_handler(text=["Месяц"])
async def statisticUserMonth(message: types.Message, state: FSMContext):
    user_id = message.from_user.id  # ID чата
    premium_end = await database.checkPremiumIsEnd(user_id)
    if premium_end:
        await premiumIsEnd(user_id=user_id, state=state)
    else:
        picture = await statistics.analiticData(user_id, "month")  # путь к картинке со статой
        if isinstance(picture, BytesIO):
            # await message.answer("Ваша статистика за месяц")
            sent_message = await bot.send_photo(chat_id=message.chat.id, photo=picture)

            # message_id = await database.getMessageId(user_id, "stat_month")
            # if message_id is not None:
            #     try:
            #         await bot.delete_message(chat_id=user_id, message_id=message_id)
            #     except Exception as e:
            #         print(f"Не удалось удалить сообщение с ID {message_id}: {e}")
            # message_id = sent_message.message_id
            # await database.addMessageId(user_id, "stat_month", message_id)


            picture = None  # Убираем ссылку на объект и освобождаем память
        else:
            await message.answer("Недостаточно данных. Возможно вы еще не ввели смайлики за этот период.")


@dp.message_handler(text=["Все время"])
async def statisticUserAll(message: types.Message, state: FSMContext):
    user_id = message.from_user.id  # ID чата
    premium_end = await database.checkPremiumIsEnd(user_id)
    if premium_end:
        await premiumIsEnd(user_id=user_id, state=state)
    else:
        picture = await statistics.analiticData(user_id, "all")  # путь к картинке со статой
        if isinstance(picture, BytesIO):
            sent_message = await bot.send_photo(chat_id=message.chat.id, photo=picture)

            # message_id = await database.getMessageId(user_id, "stat_alltime")
            # if message_id is not None:
            #     try:
            #         await bot.delete_message(chat_id=user_id, message_id=message_id)
            #     except Exception as e:
            #         print(f"Не удалось удалить сообщение с ID {message_id}: {e}")
            # message_id = sent_message.message_id
            # await database.addMessageId(user_id, "stat_alltime", message_id)

            picture = None  # Убираем ссылку на объект и освобождаем память
        else:
            await message.answer("Недостаточно данных. Возможно вы еще не ввели смайлики за этот период.")


def show_fake_inline_button(emoji_list, selected_emojis=[], date_offset=0):
    """ Создает инлайн-кнопки, которые не влияют на базу данных,
        для визуального отображения выбора в статистике за день.

        Также, добавляет кнопки перелистывания даты в виде стрелок. """
    buttons = [InlineKeyboardButton(emoji + "✅" if emoji in selected_emojis else emoji, callback_data="fake_buttons")
               for emoji in emoji_list]
    button1 = InlineKeyboardButton("⬅️", callback_data=f"fake_left_arrow_{date_offset}")
    button2 = InlineKeyboardButton("➡️", callback_data=f"fake_right_arrow_{date_offset}")

    keyboard = InlineKeyboardMarkup(row_width=5)
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
    # получаем из базы message_id

    msg_id = await database.getMessageId(user_id, "stat_day")

    smile_list = smileys + await database.getPersonalSmiles(user_id)

    async def pastPicture():
        """
        Функция для отправки картинки с отсутствием данных
        """
        picture = pictureNoData.createPictureNoData(user_id, new_date)
        input_media = InputMediaPhoto(media=picture)

        await bot.edit_message_media(
            chat_id=user_id,
            message_id=msg_id,
            media=input_media,
            reply_markup=show_fake_inline_button(smile_list, date_offset=date_offset)
        )
        picture = None  # Убираем ссылку на объект и освобождаем память


    # Получаем текущую дату и применяем смещение
    new_date = str(date.today() + timedelta(days=date_offset))

    """ Проверяем на наличие данных по указанному дню в базе 
    и при положительном ответе изменяем сообщение с добавлением новой статистики """
    try:
        userSmiles = await database.getSmileInfo(user_id, new_date)
        picture = await statistics.analiticData(user_id, "day", new_date)  # путь к картинке со статой
        if isinstance(picture, BytesIO):
            input_media = InputMediaPhoto(media=picture)

            await bot.edit_message_media(
                chat_id=user_id,
                message_id=msg_id,
                media=input_media,
                reply_markup=show_fake_inline_button(smile_list, userSmiles, date_offset)
            )
            picture = None  # Убираем ссылку на объект и освобождаем память
        else:
            await pastPicture()
    except KeyError:
        await pastPicture()


# -----------------------------------------------------------------------------------------------------------------------
"""Добавление смайлика к таблице выбора"""


# -----------------------------------------------------------------------------------------------------------------------


@dp.message_handler(text=["Добавить смайлик"])
async def addSmileToMenu(message: types.Message):
    await message.answer("Выберите действие", reply_markup=show_button(buttons_addSmileToMenu))


@dp.message_handler(text=["Добавить"])
async def addSmile(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    premium_end = await database.checkPremiumIsEnd(user_id)
    if premium_end:
        await premiumIsEnd(user_id=user_id, state=state)
    else:
        personal_smiles = await database.getPersonalSmiles(message.from_user.id)
        if len(personal_smiles) < 10:
            await message.answer("Отправьте смайлик, который вы хотите добавить. Премиум смайлики добавлять нельзя.",
                                 reply_markup=show_button(["Вернуться"]))
            await UserState.personal_smile_add.set()
            await database.setUserState(message.from_user.id, 'personal_smile_add')
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

    if len(personal_smile) == 1 and contains_emojis(personal_smile):
        if personal_smile in smile_list:
            await message.answer(f"{personal_smile} - такой смайлик уже есть. Выберите другой.")
        else:
            await message.answer(f"Смайл {personal_smile} добавлен ✅")
            await database.addPersonalSmiles(user_id, personal_smile)
            await state.set_state(None)
            await database.setUserState(user_id, None)
            await message.answer('Выбери что тебя интересует', reply_markup=show_button(buttons_menu))
    elif personal_smile == 'Вернуться':
        await state.set_state(None)
        await database.setUserState(user_id, None)
        await message.answer('Выбери что тебя интересует', reply_markup=show_button(buttons_menu))
    elif len(personal_smile) > 1 and contains_emojis(personal_smile):
        await message.answer(
            "Неправильный ввод! \nПохоже, вы использовали специальный смайлик, который может быть доступен только на определенных "
            "устройствах. \nПовторите попытку или нажмите 'Вернуться'.", reply_markup=show_button(["Вернуться"]))
    else:
        await message.answer("Неправильный ввод! \nВозможно, вы отправили специальный смайлик, который может быть "
                             "доступен только на определенных устройствах, или вы отправили текст. \n"
                             "Повторите попытку или нажмите 'Вернуться'.", reply_markup=show_button(["Вернуться"]))


@dp.message_handler(text=["Удалить"])
async def deleteSmile(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    premium_end = await database.checkPremiumIsEnd(user_id)
    if premium_end:
        await premiumIsEnd(user_id=user_id, state=state)
    else:
        personal_smiles = await database.getPersonalSmiles(message.from_user.id)
        if len(personal_smiles) > 0:
            await message.answer("Отправьте смайлик, который вы хотите удалить.", reply_markup=show_button(["Вернуться"]))
            await UserState.personal_smile_remove.set()
            await database.setUserState(message.from_user.id, 'personal_smile_remove')
        else:
            await message.answer("Вы не добавили ни одного смайлика. "
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

    if len(personal_smile) == 1 and contains_emojis(personal_smile):
        if personal_smile in smileys:
            await message.answer(f"{personal_smile} - этот смайлик находится в стандартном меню выбора, "
                                 f"его нельзя удалять. Выберите другой.", reply_markup=show_button(["Вернуться"]))
        elif not personal_smile in smile_list:
            await message.answer(
                f"{personal_smile} - этого смайлика нет в добавленных вами смайликах. Выберите другой.",
                reply_markup=show_button(["Вернуться"]))
        else:
            await message.answer(f"Смайл {personal_smile} удален ✅")
            await database.removePersonalSmile(user_id, personal_smile)
            await state.set_state(None)
            await database.setUserState(user_id, None)
            await message.answer('Выбери что тебя интересует', reply_markup=show_button(buttons_menu))
    elif personal_smile == 'Вернуться':
        await state.set_state(None)
        await database.setUserState(user_id, None)
        await database.setUserState(user_id, None)
        await message.answer('Выбери что тебя интересует', reply_markup=show_button(buttons_menu))
    else:
        await message.answer("Неправильный ввод! Отправьте смайлик.\n"
                             "Если вы не хотите отправлять смайл, то выберите: 'Вернуться'",
                             reply_markup=show_button(["Вернуться"]))


# -----------------------------------------------------------------------------------------------------------------------
"""Генерация портрета с помощью chatGPT"""


# -----------------------------------------------------------------------------------------------------------------------


@dp.message_handler(text=["Сгенерировать портрет"])
async def generationPortrait(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    is_premium = await database.checkPremiumUser(message.from_user.id)
    premium_end = await database.checkPremiumIsEnd(user_id)
    if is_premium and not premium_end:
        await message.answer("Выбери за какой период ты хочешь сгенерировать психологический портрет.",
                             reply_markup=show_button(["За день", "За неделю", "Вернуться"]))
    elif is_premium and premium_end:
        await premiumIsEnd(user_id=user_id, state=state)
    else:
        await message.answer(
            "Для использования генерации психологического портрета с помощью chatGPT необходимо приобрести подписку\n"
            "Выберите срок подписки:", reply_markup=show_button(premium_list_default))


@dp.message_handler(text=["За день"])
async def generationPortraitDay(message: types.Message, state: FSMContext):
    """
    Отправляет пользователю сгенерированный психологический портрет chatGPT за день. Если пользователь не вводил смайлики
    сегодня или вызывал команду генерации портрета более 2 раз, то он не генерируется.
    """
    user_id = message.from_user.id
    is_premium = await database.checkPremiumUser(user_id)
    premium_end = await database.checkPremiumIsEnd(user_id)
    if is_premium and not premium_end:
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
            await message.answer(
                "Превышен лимит использований команды на сегодня. Попробуйте сгенерировать портрет завтра")
    elif is_premium and premium_end:
        await premiumIsEnd(user_id=user_id, state=state)


@dp.message_handler(text=["За неделю"])
async def generationPortraitWeek(message: types.Message, state: FSMContext):
    """
    Отправляет пользователю сгенерированный психологический портрет chatGPT за неделю. Если пользователь не вводил смайлики
    хотя бы 7 дней или вызывал эту команду более 2 раз, то портрет не генерируется.
    """
    user_id = message.from_user.id
    is_premium = await database.checkPremiumUser(user_id)
    premium_end = await database.checkPremiumIsEnd(user_id)
    if is_premium and not premium_end:
        if await database.getUsedGPT(user_id) < 2:

            smilesDict = await database.getSmileInfo(user_id, "all")
            count = statistics.day_counter(7, smilesDict)
            if count <= 1:
                await message.answer("Слишком мало информации. Для получения портрета необходимо выбрать смайлик"
                                     , reply_markup=show_button(buttons_menu))
            else:
                await message.answer("Портрет генерируется. Дождитесь завершения.",
                                     reply_markup=types.ReplyKeyboardRemove())
                smilesDict = converting_dates_to_days(dict(list(smilesDict.items())[-count:]))
                smiles = '\n'.join('{}: {}'.format(key, val) for key, val in smilesDict.items())  # Словарь в строку

                portrait = await database.getExistingPortrait(smiles, "week")
                if portrait == "NotExist":
                    portrait = await chatGPT.create_psychological_portrait_week(", ".join(smiles))
                    await database.addPortrait(smiles, portrait, "week")
                await message.answer(f'<b>Количество дней когда вы выбирали смайлики за последнюю неделю:{count}</b> \n\n {portrait}', reply_markup=show_button(buttons_menu), parse_mode="HTML")
                await database.addUsedGPT(user_id)
        else:
            await message.answer(
                "Превышен лимит использований команды на сегодня. Попробуйте сгенерировать портрет завтра")
    elif is_premium and premium_end:
        await premiumIsEnd(user_id=user_id, state=state)


# -----------------------------------------------------------------------------------------------------------------------
"""Остальные"""


# -----------------------------------------------------------------------------------------------------------------------


def show_button(list_menu):
    """Принимает список и превращает его в кнопки"""
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(*list_menu)
    return keyboard


def show_inline_button(emoji_list, selected_emojis=[]):
    buttons = [InlineKeyboardButton(emoji + "✅" if emoji in selected_emojis
                                    else emoji, callback_data=emoji) for emoji in emoji_list]
    return InlineKeyboardMarkup(row_width=5).add(*buttons)


def add_checkmark(lst, variable):
    return [elem + "✅" if elem == variable else elem for elem in lst]


@dp.message_handler(text=["Выбрать смайлик"])
async def show_emoji(message: types.Message):
    emoji_list = smileys + await database.getPersonalSmiles(message.from_user.id)
    prevSmileMsg = await database.getPrevSmileMsgID(message.from_user.id)
    smileListToDay = ''
    if prevSmileMsg is not None:
        await delMessage(message.chat.id, prevSmileMsg)
        smileListToDay = await database.getSmileInfo(message.from_user.id, str(date.today()))
        for i in smileListToDay:
            emoji_list = add_checkmark(emoji_list, i)

    smile_msg = await message.reply(f'<b>Выбранные смайлики:</b>\n{"".join(smileListToDay)}',
                                    reply_markup=show_inline_button(emoji_list), parse_mode="HTML")

    await database.updateSmileMsgID(message.from_user.id, smile_msg["message_id"])


@dp.callback_query_handler()
async def button(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    limit_end = await database.emojiLimitExpired(user_id)
    is_premium = await database.checkPremiumUser(user_id)
    premium_end = await database.checkPremiumIsEnd(user_id)
    if is_premium and premium_end:
        await premiumIsEnd(user_id=user_id, state=state)
    elif limit_end and not is_premium:
        prevSmileMsg = await database.getPrevSmileMsgID(user_id)
        if prevSmileMsg is not None:
            await delMessage(callback_query.message.chat.id, prevSmileMsg)
        await set_state(user_id, state=state)

    else:
        # Лист с выбранными смайликами за день
        selected_emojis = await database.getSmileInfo(user_id, str(date.today()))
        selected_emoji = callback_query.data

        if '✅' in selected_emoji:
            selected_emoji = selected_emoji.removesuffix('✅')
        # Проверяем, есть ли выбранный смайлик уже в списке выбранных
        if selected_emoji not in selected_emojis:
            # Если смайлика еще нет в списке выбранных, добавляем его
            selected_emojis.append(selected_emoji)
            await callback_query.answer("Вы выбрали смайлик ✅")
            await database.addEmojiUsed(callback_query.from_user.id)
        else:
            # Если смайлик уже есть в списке выбранных, удаляем его, чтобы пользователь мог снова выбрать
            selected_emojis.remove(selected_emoji)
            await callback_query.answer("Смайлик снят ❌")

        print(selected_emojis)
        await database.addOrChangeSmile(callback_query.from_user.id, str(date.today()), selected_emojis)

        emoji_list = smileys + await database.getPersonalSmiles(user_id)
        await callback_query.message.edit_text(
            "Выбранные смайлики:\n" + "".join(
                selected_emojis) if selected_emojis else "Выбранных смайликов пока нет",
            reply_markup=show_inline_button(emoji_list, selected_emojis)
        )


async def set_state(user_id, state: FSMContext):
    await state.set_state(UserState.limit_is_over.state)
    await database.setUserState(user_id, 'limit_is_over')
    await bot.send_message(user_id, 'Вы использовали свой лимит в 100 смайликов, чтобы продолжить вам необходимо '
                                    'приобрести premium подписку, выберете подписки',
                           reply_markup=show_button(premium_list_state))


@dp.message_handler(commands=['admin'])
async def admin(message: types.Message):
    if message.from_user.id in config.ADMIN_ID:
        await message.answer('Выполнен вход в админ-панель', reply_markup=show_button(admin_menu))


@dp.message_handler(text=["Кол-во новых пользователей за неделю"])
async def stat_new_week(message: types.Message):
    if message.from_user.id in config.ADMIN_ID:
        await message.answer(f'Кол-во новых пользователей за неделю: {await database.getCountNewUsers()}',
                             reply_markup=show_button(admin_menu))


@dp.message_handler(text=["Общее кол-во пользователей"])
async def stat_all(message: types.Message):
    if message.from_user.id in config.ADMIN_ID:
        await message.answer(f'Общее кол-во пользователей: {await database.getCountAllUsers()}',
                             reply_markup=show_button(admin_menu))


@dp.message_handler(text=["Статистика за день"])
async def stat_day(message: types.Message):
    if message.from_user.id in config.ADMIN_ID:
        info = await database.getStatAdmin(1)
        await message.answer(f'Статистика за день: \n{" ".join(info)}', reply_markup=show_button(admin_menu))


@dp.message_handler(text=["Статистика за неделю"])
async def stat_week(message: types.Message):
    if message.from_user.id in config.ADMIN_ID:
        info = await database.getStatAdmin(7)
        await message.answer(f'Статистика за неделю: \n{" ".join(info)}', reply_markup=show_button(admin_menu))


@dp.message_handler(text=["Статистика за месяц"])
async def stat_month(message: types.Message):
    if message.from_user.id in config.ADMIN_ID:
        info = await database.getStatAdmin(30)
        await message.answer(f'Статистика за месяц: \n{" ".join(info)}', reply_markup=show_button(admin_menu))


@dp.message_handler(text=["Выйти"])
async def admin_exit(message: types.Message):
    if message.from_user.id in config.ADMIN_ID:
        await message.reply('Выход из админ-панели', reply_markup=show_button(buttons_menu))


@dp.pre_checkout_query_handler(lambda query: True)
async def pre_checkout_query(pre_checkout_q: types.PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_q.id, ok=True)


@dp.message_handler(content_types=ContentType.SUCCESSFUL_PAYMENT)
async def successful_payment(message: types.Message, state: FSMContext):
    print("SUCCESSFUL PAYMENT")

    prevInvoiceMsg = await database.getPrevInvoiceMsgID(message.chat.id)
    if prevInvoiceMsg is not None:
        await delMessage(message.chat.id, prevInvoiceMsg)

    await state.set_state(None)
    await database.setUserState(message.from_user.id, None)
    payment_info = message.successful_payment.to_python()
    for k, v in payment_info.items():
        print(f"{k}={v}")

    await message.answer(
        "Платеж на сумму {:.2f} {} прошел успешно".format(float(message.successful_payment.total_amount) / 100,
                                                          message.successful_payment.currency),
        reply_markup=show_button(buttons_menu))

    current_date = datetime.today()

    if message.successful_payment.total_amount / 100 == 100:
        data_end = current_date + timedelta(days=31)
    elif message.successful_payment.total_amount / 100 == 200:
        data_end = current_date + timedelta(days=182)
    else:
        data_end = current_date + timedelta(days=365)

    await database.premiumStatus(message.from_user.id, str(data_end.date()))

    await message.answer(await database.infoPremiumUser(message.from_user.id))


async def delMessage(chat_id: int, msgID: int):
    try:
        await bot.delete_message(chat_id, msgID)
    except MessageToDeleteNotFound:
        pass
    except MessageCantBeDeleted:
        pass


async def premiumIsEnd(user_id: int, state: FSMContext):
    await state.set_state(UserState.limit_is_over.state)
    await database.setUserState(user_id, 'limit_is_over')
    await database.removePremiumStatus(user_id)
    await bot.send_message(chat_id=user_id,
                           text="Срок вашей премиум подписки подошёл к концу, для дальнейшего использование бота "
                                "необходимо приобрести подписку", reply_markup=show_button(premium_list_state))


async def setUserStateFromDB():
    UserStates = await database.getUsersState()
    if UserStates is not None:
        for key, value in UserStates.items():
            state_obj = dp.current_state(chat=key, user=key)
            if value == "limit_is_over":
                state_to_set = UserState.limit_is_over
                await state_obj.set_state(state_to_set)
                print(f'Установлено limit_is_over для {key}')
            elif value == "personal_smile_add":
                state_to_set = UserState.personal_smile_add
                await state_obj.set_state(state_to_set)
                print(f'Установлено personal_smile_add для {key}')
            elif value == "personal_smile_remove":
                state_to_set = UserState.personal_smile_remove
                await state_obj.set_state(state_to_set)
                print(f'Установлено personal_smile_remove для {key}')
            elif value == "None":
                state_to_set = None
                await state_obj.set_state(None)


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
