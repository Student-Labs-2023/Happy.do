from PIL import Image, ImageDraw, ImageFont
import os

def createPictureNoData(ID, date):

    # Настройки изображения
    width, height = 400, 200
    text_color = (0, 0, 0)  # Черный текст
    font_size = 30

    # Загрузка изображения фона
    background_image = Image.open(os.getcwd() + r"\tgbot\utiles\Statistics\Config\logo3 (2).jpg")
    background_image = background_image.resize((width, height))

    # Создание объекта рисования
    draw = ImageDraw.Draw(background_image)

    # # Загрузка шрифта (замените путь на нужный)
    # font_path = "/путь/к/шрифту.ttf"
    # font = ImageFont.truetype(font_path, font_size)

    # Подготовка текста для вставки
    text = f"{date} - Нет данных"

    # Определение размера текста для центрирования
    text_width, text_height = draw.textsize(text)
    x = (width - text_width) // 2
    y = (height - text_height) // 2

    # Вставка текста на изображение
    draw.text((x, y), text, fill=text_color)

    # Сохранение изображения с текстом
    result_image_path = os.getcwd() + fr"\tgbot\utiles\Statistics\Picture\ImageNoData{ID}.jpg"
    background_image.save(result_image_path)

    return result_image_path

