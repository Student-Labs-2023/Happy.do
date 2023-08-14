import datetime
from collections import Counter
from datetime import date
from datetime import datetime, timedelta
from tgbot.utiles import database
from tgbot.utiles.Statistics import diagrams


async def compilingList(list: []):
    newList = []
    for smile in list:
        if ", " in smile:
            newList.extend(smile.split(", "))
        else:
            newList.append(smile)

    return newList

def day_counter(period, smilesDict):
    """
        Функция day_counter используется для получения информации о дате от которой начинать брать статистику из БД.

        :param period: за какой период хотят взять статистику (31 или 7) в днях
        :return: Количество дней которые надо взять из БД
        """
    last_period_dates = []
    current_day = date.today()
    for i in range(period):
        last_period_dates.append(str(current_day))
        current_day -= timedelta(days=1)
    smilesListKeys = list(smilesDict.keys())

    last_month_date = last_period_dates.copy().pop()
    kol = 0
    for i in smilesListKeys:
        if datetime.strptime(last_month_date, "%Y-%m-%d") < datetime.strptime(i, "%Y-%m-%d"):
            kol += 1

    return kol


""" Подсчитывание кол-ва одинаковых смайликов """
async def getData(ID, period, day):
    smilesDict = await database.getSmileInfo(ID, "all")
    if period == "month":


        smilesList = [smilesDict[i] for i in list(smilesDict.keys())[-day_counter(31, smilesDict):]]
        smilesList = await compilingList(smilesList)
    elif period == "week":

        smilesList = [smilesDict[i] for i in list(smilesDict.keys())[-day_counter(7, smilesDict):]]
        smilesList = await compilingList(smilesList)
    elif period == "day":
        try:
            smilesList = smilesDict[day].split(", ")
            smilesList = await compilingList(smilesList)
        except KeyError:
            raise ValueError
    else:
        smilesList = [smilesDict[i] for i in smilesDict]
        smilesList = await compilingList(smilesList)

    cnt = Counter()
    for smile in smilesList:
        cnt[smile] += 1
    return cnt


async def analiticData(ID, period, day=str(date.today())):
    try:
        smiles = await getData(ID, period, day)  # словарь со статистикой по смайлам
    except ValueError:
        return "absent"

    summ = 0  # сумма всех значений

    """ Разделение словаря на два списка """
    keys = [i for i in smiles]
    values = [smiles[i] for i in smiles]


    if len(smiles) > 5: size = 6
    elif len(smiles) > 0: size = len(smiles)
    else: return "absent"

    maxValues = sorted(values, reverse=True)[: 4 if size == 6 else size]  # максимальные значения
    maxKeys = []  # ключи максимальных значений

    """ Получаем id макс значений """
    for i in range(len(values)):
        if (values[i] in maxValues) and (len(maxKeys) < 4 if size == 6 else 5):
            maxKeys.append(keys[i])
        summ += values[i]

    """ Перезаписываем список в правильном порядке """
    for i in range(4 if size == 6 else size):
        maxValues[i] = smiles[maxKeys[i]]

    """ Части в процентном соотношении """
    sizes = [round(maxValues[i] / summ, 2) for i in range(4 if size == 6 else size)]
    if size == 6:
        sizes.append(round((summ - sum(maxValues)) / summ, 2))
        maxKeys.append('Другие')

    """ Вызов создания круговой диаграммы """
    return diagrams.createCircularChart(ID, maxKeys, sizes, day if period == 'day' else '')

