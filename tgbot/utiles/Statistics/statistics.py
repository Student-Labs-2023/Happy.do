from tgbot.utiles.Statistics import diagrams


def analiticData(ID):
    smiles = {'😀': 1, '😂': 8, '😍': 50, '😊': 1, '😢': 7, '😡': 3, '🙄': 4}  # FOR TESTING

    keys = []
    values = []
    summ = 0  # сумма всех значений

    """ Разделяем словарь на два списка """
    for i in smiles:
        keys.append(i)
        values.append(smiles[i])

    maxValues = sorted(values, reverse=True)[:4]  # максимальные значения
    maxKeys = []  # ключи максимальных значений

    """ Получаем id макс значений """
    for i in range(len(values)):
        if values[i] in maxValues:
            maxKeys.append(keys[i])
        summ += values[i]

    """ Перезаписываем список в правильном порядке """
    for i in range(4):
        maxValues[i] = smiles[maxKeys[i]]

    """ Части в процентном соотношении """
    sizes = [round(maxValues[0] / summ, 1), round(maxValues[1] / summ, 1), round(maxValues[2] / summ, 1),
             round(maxValues[3] / summ, 1), (summ - sum(maxValues)) / summ]
    maxKeys.append('Другие')

    """ Вызов создания круговой диаграммы """
    return diagrams.createCircularChart(ID, maxKeys, sizes)
