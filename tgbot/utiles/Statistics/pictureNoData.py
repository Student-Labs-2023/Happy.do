from PIL import Image, ImageDraw, ImageFont
import os

def createPictureNoData(ID, date):

    # Настройки изображения
    width, height = 700, 700
    text_color = (255, 255, 255)  # Белый текст
    font_size = 40

    # Загрузка изображения фона
    background_image = Image.open(os.getcwd() + r"\tgbot\utiles\Statistics\Config\logo3 (2).jpg")
    background_image = background_image.resize((width, height))

    # Создание объекта рисования
    draw = ImageDraw.Draw(background_image)

    # Загрузка шрифта
    font_path = os.getcwd() + r"\tgbot\utiles\Statistics\Config\ofont.ru_Franklin Gothic Medium.ttf"
    font = ImageFont.truetype(font_path, font_size)

    text = f"{date} - Нет данных"

    # Вставка текста на изображение
    x = 130
    y = 100
    draw.text((x, y), text, fill=text_color, font=font)

    # Сохранение изображения с текстом
    result_image_path = os.getcwd() + fr"\tgbot\utiles\Statistics\Picture\ImageNoData{ID}.jpg"
    background_image.save(result_image_path)

    return result_image_path

