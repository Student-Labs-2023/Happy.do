import asyncio
from collections import Counter
from tgbot.utiles import database
from tgbot.utiles.Statistics import diagrams


""" Подсчитывание кол-ва одинаковых смайликов """
async def getData(ID):
    smilesDict = await database.getSmileInfo(ID, "all")
    smilesList = [smilesDict[i] for i in smilesDict]

    cnt = Counter()
    for smile in smilesList:
        cnt[smile] += 1
    return cnt


async def analiticData(ID):
    smiles = await getData(ID)  # словарь со статистикой по смайлам
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
        if values[i] in maxValues:
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
    sizes = [round(maxValues[i] / summ, 1) for i in range(4 if size == 6 else size)]
    if size == 6:
        sizes.append((summ - sum(maxValues)) / summ)
        maxKeys.append('Другие')
    print(sizes)

    """ Вызов создания круговой диаграммы """
    return diagrams.createCircularChart(ID, maxKeys, sizes)

# analiticData(1093031870)