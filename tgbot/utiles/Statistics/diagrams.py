from io import BytesIO

from PIL import Image

import matplotlib.pyplot as plt
import matplotlib
import numpy as np
from matplotlib.font_manager import FontProperties

from tgbot.utiles.firebaseStorage import download_file_to_RAM

""" Круговая диаграмма """


def createCircularChart(ID, labels, sizes, day):
    """
    Функция createCircularChart используется для создания круговых диаграмм статистики.

    :param ID: ID пользователя.
    :param labels: Названия частей (смайлики и если больше 5 значений, то доп секция "Другие").
    :param sizes: Размеры каждой части.
    :param day: День для указания его в лейбле.
    :return: Картинку в виде байтов сохраненную в оперативке.
    """

    plt.style.use(
        "https://firebasestorage.googleapis.com/v0/b/happydo-7c1a5.appspot.com/o/pitayasmoothie-dark.mplstyle?alt=media&token=967d45d0-f2e1-46a3-91a1-1e5a655875a7")  # Утанавливает стиль

    prop2 = FontProperties(fname="Fonts/NotoEmoji-Medium.ttf")
    prop3 = FontProperties(fname="Fonts/DejavuserifcondensedBolditalic.ttf")
    prop1 = FontProperties(fname="Fonts/Seguiemj.ttf")
    propTitle = FontProperties(fname="Fonts/FranklinGothicMedium.ttf")

    matplotlib.rcParams['font.family'] = [prop1.get_name(), prop2.get_name(), prop3.get_name(),
                                          "DejaVu Sans"]  # Меняет шрифт в стиле
    matplotlib.rcParams['font.size'] = 14

    fig, ax = plt.subplots()  # устанавливает размеры гистограммы

    ax.set_title(f"Наиболее часто используемые смайлики\n{day}", fontsize=15,
                 fontname=propTitle.get_name())  # заголовок гистограммы

    """ Диаграмма """
    # цвета
    cmap = plt.colormaps["tab10"]
    outer_colors = cmap(np.arange(5) * 1)
    # свойства диаграммы (sizes - размеры каждой части, labels - названия частей,
    # autopct - формат инфы, pctdistance - дистанция от центра инфы, radius - размер диаграммы
    ax.pie(sizes, labels=labels, autopct='%1.1f%%', pctdistance=0.8, radius=1, colors=outer_colors,
           wedgeprops=dict(width=0.4, edgecolor='w'))

    file_data = download_file_to_RAM("logo.jpg")
    img = Image.open(BytesIO(file_data.read()))
    ax.imshow(img, zorder=0, extent=[-0.695, 0.705, -0.65, 0.75])

    picture = BytesIO()
    fig.savefig(picture, transparent=False, dpi=200,
                bbox_inches="tight")  # сохранение картинки
    picture.seek(0)

    plt.close(fig)

    return picture
