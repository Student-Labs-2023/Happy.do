import matplotlib.pyplot as plt
import matplotlib, os
import numpy as np


""" Круговая диаграмма """
def createCircularChart(ID, labels, sizes, day):
    plt.style.use(
        fr"{os.getcwd()}\tgbot\utiles\Statistics\Config\pitayasmoothie-dark.mplstyle")  # Утанавливает стиль
    matplotlib.rcParams['font.family'] = ["Segoe UI Emoji", "DejaVu Sans"]  # Меняет шрифт в стиле
    matplotlib.rcParams['font.size'] = 13  # Меняет размер шрифта в стиле
    fig, ax = plt.subplots()  # устанавливает размеры гистограммы

    ax.set_title(f"Наиболее часто используемые смайлики\n{day}", fontsize=15,
                 fontname="Franklin Gothic Medium")  # заголовок гистограммы

    """ Диаграмма """
    # цвета
    cmap = plt.colormaps["tab10"]
    outer_colors = cmap(np.arange(5) * 1)
    # свойства диаграммы (sizes - размеры каждой части, labels - названия частей,
    # autopct - формат инфы, pctdistance - дистанция от центра инфы, radius - размер диаграммы
    ax.pie(sizes, labels=labels, autopct='%1.1f%%', pctdistance=0.8, radius=1, colors=outer_colors,
           wedgeprops=dict(width=0.4, edgecolor='w'))

    img = plt.imread(os.getcwd() + r"\tgbot\utiles\Statistics\Config\logo3 (2).jpg")
    ax.imshow(img, zorder=0, extent=[-0.695, 0.705, -0.65, 0.75])

    fig.savefig(os.getcwd() + fr'\tgbot\utiles\Statistics\Picture\circular{str(ID)}.jpg', transparent=False, dpi=200,
                bbox_inches="tight")  # сохранение картинки

    # plt.clf()
    plt.close(fig)

    return fr"{os.getcwd()}\tgbot\utiles\Statistics\Picture\circular{str(ID)}.jpg"



""" Гистограмма """
def createBarChart(ID, labels, days, day):
    plt.style.use(
        fr"{os.getcwd()}\tgbot\utiles\Statistics\Config\pitayasmoothie-dark.mplstyle")  # Утанавливает стиль
    matplotlib.rcParams['font.family'] = ["Segoe UI Emoji", "DejaVu Sans"]  # Меняет шрифт в стиле
    matplotlib.rcParams['font.size'] = 13  # Меняет размер шрифта в стиле
    fig, ax = plt.subplots()  # устанавливает размеры гистограммы

    plt.suptitle(f"Наиболее часто используемые смайлики\n{day}", fontname="Franklin Gothic Medium",
                 fontsize=20)

    """ Статистика по наиболее часто используемым смайликам """
    ax.bar(labels, days)  # создание гистограммы


    ax.set_xlabel('Smiles', fontsize=15)
    ax.set_ylabel('Days', fontsize=15)
    ax.set_ylim(-0.5, 30)  # разлиновка по у

    fig.savefig(os.getcwd() + r'\tgbot\utiles\Statistics\Picture\Bar.png', transparent=False, dpi=80,
                bbox_inches="tight")  # сохранение картинки

    # plt.clf()
    plt.close(fig)


    return rf"{os.getcwd()}\tgbot\utiles\Statistics\Picture\Bar{str(ID)}.jpg"

