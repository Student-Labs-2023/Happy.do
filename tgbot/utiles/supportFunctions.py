from datetime import datetime

from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeDefault


async def set_commands(bot: Bot):
    commands = [
        BotCommand(
            command='start',
            description='Начало работы'
        ),
        BotCommand(
            command='stats',
            description='📊Статистика'
        ),
        BotCommand(
            command='choice',
            description='😄Выбрать смайлик'
        ),
        BotCommand(
            command='add',
            description='➕Добавить смайлик'
        ),
        BotCommand(
            command='generate',
            description='🖼️Сгенерировать портрет'
        ),
        BotCommand(
            command='premium',
            description='💎Приобрести премиум подписку'
        ),
        BotCommand(
            command='cancel',
            description='Отменить действие'
        )
    ]

    await bot.set_my_commands(commands, BotCommandScopeDefault())


def converting_dates_to_days(dates_dict: {}) -> {}:
    """
    Функция converting_dates_to_days используется для конвертирования словаря из дат со смайликами в словарь
    форматом {"<количество дней назад>": "<смайлики>"},

    :param dates_dict: Прежний словарь со смайликами.
    :return: Новый словарь со смайликами.
    """
    today = datetime.now()
    new_dict = {
        str((today - datetime.strptime(day, '%Y-%m-%d')).days) if (today - datetime.strptime(day,
                                                                                             '%Y-%m-%d')).days != 0 else "Сегодня": value
        for day, value in dates_dict.items()
    }
    return new_dict
