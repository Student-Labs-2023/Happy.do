from collections import Counter
from datetime import date

from tgbot.utiles import database
from tgbot.utiles.Statistics import diagrams


""" Подсчитывание кол-ва одинаковых смайликов """
async def getData(ID, period):
    smilesDict = await database.getSmileInfo(ID, "all")

    if period == "month":
        if len(smilesDict) < 31:
            raise ValueError
        else:
            smilesList = [smilesDict[i] for i in list(smilesDict.keys())[-31:]]
    elif period == "week":
        if len(smilesDict) < 7:
            raise ValueError
        else:
            smilesList = [smilesDict[i] for i in list(smilesDict.keys())[-7:]]
    elif period == "day":
        smilesList = smilesDict[str(date.today())]
    else:
        smilesList = [smilesDict[i] for i in smilesDict]

        # month = date_day[-5:-3]
        # day = date_day[-2:]
        # for i in range(day, 3)
        # dateStart = f"{date_day[:4]}-{int(month)-1}-{day}" # дата того же числа прошлого месяца
        # if dateStart in smilesDict:

    cnt = Counter()
    for smile in smilesList:
        cnt[smile] += 1
    return cnt


async def analiticData(ID, period):
    try:
        smiles = await getData(ID, period)  # словарь со статистикой по смайлам
    except ValueError:
        return "absent"

    print(smiles)
    summ = 0  # сумма всех значений

    """ Разделение словаря на два списка """
    keys = [i for i in smiles]
    values = [smiles[i] for i in smiles]


    if len(smiles) > 5: size = 6
    elif len(smiles) > 0: size = len(smiles)
    else: return "absent"

    maxValues = sorted(values, reverse=True)[: 4 if size == 6 else size]  # максимальные значения
    maxKeys = []  # ключи максимальных значений
    print(maxValues)


    """ Получаем id макс значений """
    for i in range(len(values)):
        if (values[i] in maxValues) and (len(maxKeys) < 4 if size == 6 else 5):
            maxKeys.append(keys[i])
        summ += values[i]
    print(maxKeys)
    print(summ)

    """ Перезаписываем список в правильном порядке """
    for i in range(4 if size == 6 else size):
        # if (i >= len(smiles)): break
        maxValues[i] = smiles[maxKeys[i]]

    print(maxValues)


    """ Части в процентном соотношении """
    sizes = [round(maxValues[i] / summ, 2) for i in range(4 if size == 6 else size)]
    if size == 6:
        sizes.append(round((summ - sum(maxValues)) / summ, 2))
        maxKeys.append('Другие')
    print(sizes)

    """ Вызов создания круговой диаграммы """
    return diagrams.createCircularChart(ID, maxKeys, sizes)

