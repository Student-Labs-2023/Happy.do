from datetime import datetime
import demoji


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
