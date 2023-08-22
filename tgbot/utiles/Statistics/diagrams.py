from io import BytesIO
from pathlib import Path

from PIL import Image


import matplotlib.pyplot as plt
import matplotlib, os
import numpy as np
from matplotlib import font_manager
from matplotlib.font_manager import FontProperties
# import matplotlib.font_manager as fm


from tgbot.utiles.firebaseStorage import download_file_to_RAM

""" Круговая диаграмма """
def createCircularChart(ID, labels, sizes, day):
    # """
    # Функция createCircularChart используется для создания круговых диаграмм статистики.
    #
    # !!!Если шрифты не работают!!!
    # Чтобы работали шрифты, необходимо предварительно добавить шрифты в формате .ttf в папку (в проекте уже имеются)
    # \venv\Lib\site-packages\matplotlib\mpl-data\fonts\ttf.
    # Затем удалить кеш (единственный файл) в папке С:\windows\users\<user>\.matplotlib\<file>.
    # Далее, после запуска скрипта, создастся новый файл с кешом, который уже будет иметь эти шрифты.
    #
    # Для докер-образа также нужно удалить этот файл.
    #
    # :param ID: ID пользователя.
    # :param labels: Названия частей (смайлики и если больше 5 значений, то доп секция "Другие").
    # :param sizes: Размеры каждой части.
    # :param day: День для указания его в лейбле.
    # :return: Картинку в виде байтов сохраненную в оперативке.
    # """

    # style = download_file_to_RAM(
    #     "pitayasmoothie-dark.mplstyle")
    # style.seek(0)
    plt.style.use("https://firebasestorage.googleapis.com/v0/b/happydo-7c1a5.appspot.com/o/pitayasmoothie-dark.mplstyle?alt=media&token=967d45d0-f2e1-46a3-91a1-1e5a655875a7")  # Утанавливает стиль

    # prop = FontProperties(fname="./tgbot/utiles/Statistics/Config/NotoEmoji-Medium.ttf")
    # matplotlib.rcParams['font.family'] = [prop.get_name(), "DejaVu Sans"]  # Меняет шрифт в стиле

    fpath = Path(matplotlib.get_data_path(), r"D:\Projects\python\Happy.do\tgbot\utiles\Statistics\Config\NotoEmoji-Medium.ttf")
    # font_manager._rebuild()
    # fm = matplotlib.font_manager
    # fm._get_fontconfig_fonts.cache_clear()
    print(matplotlib.get_cachedir())
    prop2 = FontProperties(fname=r"D:\Projects\python\Happy.do\tgbot\utiles\Statistics\Config\NotoEmoji-Medium.ttf")
    prop3 = FontProperties(fname=r"D:\Projects\python\Happy.do\venv\Lib\site-packages\matplotlib\mpl-data\fonts\ttf\Dejavuserifcondensed Bolditalic.ttf")
    prop1 = FontProperties(fname=r"D:\Projects\python\Happy.do\venv\Lib\site-packages\matplotlib\mpl-data\fonts\ttf\seguiemj.ttf")
    propTitle = FontProperties(fname=r"D:\Projects\python\Happy.do\venv\Lib\site-packages\matplotlib\mpl-data\fonts\ttf\ofont.ru_Franklin Gothic Medium.ttf")
    # matplotlib._rebuild()
    # matplotlib._fmcache


    # matplotlib.rcParams['font.family'] = ["serif"]  # Меняет шрифт в стиле
    print(prop1.get_name())
    matplotlib.rcParams['font.family'] = [prop1.get_name(), prop2.get_name(), prop3.get_name(), "DejaVu Sans"]  # Меняет шрифт в стиле
    matplotlib.rcParams['font.size'] = 14

    # matplotlib.rcParams['font.family'] = ["Segoe UI Emoji", "DejaVu Sans"]  # Меняет шрифт в стиле


    # fontForSmile = download_file_to_RAM("NotoEmoji-Medium.ttf")
    # font_data = BytesIO(fontForSmile.read())
    # font_manager = fm.FontManager()
    # custom_font = font_manager.ttflist.extend(fm.createFontList([font_data]))

    # matplotlib.rcParams['font.customfont'] = FontProperties(fname="https://firebasestorage.googleapis.com/v0/b/happydo-7c1a5.appspot.com/o/NotoEmoji-Medium.ttf?alt=media&token=f647d735-7d83-4918-9f97-bb17e9a990ac")

    # matplotlib.rcParams['font.size'] = 13  # Меняет размер шрифта в стиле
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

    # img = plt.imread(os.getcwd() + r"\tgbot\utiles\Statistics\Config\logo3 (2).jpg")
    file_data = download_file_to_RAM("logo.jpg")
    img = Image.open(BytesIO(file_data.read()))
    ax.imshow(img, zorder=0, extent=[-0.695, 0.705, -0.65, 0.75])

    # fig.savefig(os.getcwd() + fr'\tgbot\utiles\Statistics\Picture\circular{str(ID)}.jpg', transparent=False, dpi=200,
    #             bbox_inches="tight")  # сохранение картинки
    picture = BytesIO()
    fig.savefig(picture, transparent=False, dpi=200,
                bbox_inches="tight")  # сохранение картинки
    picture.seek(0)

    # plt.clf()
    plt.close(fig)

    # return fr"{os.getcwd()}\tgbot\utiles\Statistics\Picture\circular{str(ID)}.jpg"
    return picture


""" Гистограмма """
# def createBarChart(ID, labels, days, day):
#     plt.style.use(
#         fr"{os.getcwd()}\tgbot\utiles\Statistics\Config\pitayasmoothie-dark.mplstyle")  # Утанавливает стиль
#     matplotlib.rcParams['font.family'] = ["Segoe UI Emoji", "DejaVu Sans"]  # Меняет шрифт в стиле
#     matplotlib.rcParams['font.size'] = 13  # Меняет размер шрифта в стиле
#     fig, ax = plt.subplots()  # устанавливает размеры гистограммы
#
#     plt.suptitle(f"Наиболее часто используемые смайлики\n{day}", fontname="Franklin Gothic Medium",
#                  fontsize=20)
#
#     """ Статистика по наиболее часто используемым смайликам """
#     ax.bar(labels, days)  # создание гистограммы
#
#
#     ax.set_xlabel('Smiles', fontsize=15)
#     ax.set_ylabel('Days', fontsize=15)
#     ax.set_ylim(-0.5, 30)  # разлиновка по у
#
#     fig.savefig(os.getcwd() + r'\tgbot\utiles\Statistics\Picture\Bar.png', transparent=False, dpi=80,
#                 bbox_inches="tight")  # сохранение картинки
#
#     # plt.clf()
#     plt.close(fig)
#
#
#     return rf"{os.getcwd()}\tgbot\utiles\Statistics\Picture\Bar{str(ID)}.jpg"


# -------------------------------------------------------------------------------------------------------------

#
# from io import BytesIO
# from PIL import Image
#
# import numpy as np
# from bokeh.plotting import figure, show
# from bokeh.io.export import get_screenshot_as_png
# from bokeh.transform import cumsum
# from bokeh.palettes import Category20c
#
# from tgbot.utiles.firebaseStorage import download_file_to_RAM
#
# def createCircularChart(ID, labels, sizes, day):
#     data = {'labels': labels, 'sizes': sizes}
#     data['angle'] = [data['sizes'][i] / sum(data['sizes']) * 2 * np.pi for i in range(len(data['sizes']))]
#     data['color'] = Category20c[len(data)]
#
#     p = figure(height=350, title=f"Наиболее часто используемые смайлики\n{day}", toolbar_location=None,
#                tools="hover", tooltips="@labels: @sizes", x_range=(-0.5, 1.0))
#
#     p.wedge(x=0, y=1, radius=0.4,
#             start_angle=cumsum('angle', include_zero=True), end_angle=cumsum('angle'),
#             line_color="white", fill_color=data['color'], legend_field=data['labels'], source=data)
#
#     file_data = download_file_to_RAM("logo.jpg")
#     img = Image.open(BytesIO(file_data.read()))
#
#     p.image_url(url=[img], x=-0.695, y=-0.65, w=1.4, h=1.4, anchor="bottom_left")
#
#     png = get_screenshot_as_png(p, height=350)
#     picture = BytesIO(png)
#
#     show(p, display_toolbar=False)  # Отобразить для проверки
#
#     return picture


# import numpy as np
# import plotly.express as px
# from tgbot.utiles.firebaseStorage import download_file_to_RAM
# from PIL import Image
# from io import BytesIO
#
#
# def createCircularChart(ID, labels, sizes, day):
#     print(labels)
#     print(sizes)
#     fig = px.pie(names=labels, values=sizes, title=f"Наиболее часто используемые смайлики\n{day}",
#                  labels={'names': 'Смайлики', 'values': 'Процент'},
#                  width=800, height=600)
#
#     # Добавление изображения
#     file_data = download_file_to_RAM("logo.jpg")
#     img = Image.open(BytesIO(file_data.read()))
#     fig.add_layout_image(dict(source=img, x=0.5, y=0.5, xanchor='center', yanchor='middle', xref="paper", yref="paper",
#                               sizex=0.5, sizey=0.5))
#
#     # Сохранение графика в байтовый поток
#     picture = BytesIO()
#     fig.write_image(picture, format="jpeg", engine="kaleido", scale=2)
#     picture.seek(0)
#
#     return picture
