from aiogram.dispatcher import Dispatcher
from aiogram import Bot, types
from tgbot.config import TELEGRAM_TOKEN
from tgbot.utiles.Statistics import statistics
import os

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher(bot)

""" Отправка статистики пользователю сообщением """
@dp.message_handler(commands=["statisticUser"])
async def statisticUser(message: types.Message):
    chat_id = message.chat.id                               # ID чата
    pathToPicture = statistics(chat_id)                     # путь к картинке со статой
    stat = open(pathToPicture, 'rb')                        # открываем фото и отправляем сообщение
    await message.answer("Ваша статистика за неделю")
    await message.answer_photo(stat, caption="caption")
    os.remove(pathToPicture)                                # удаляем файл с картинкой


