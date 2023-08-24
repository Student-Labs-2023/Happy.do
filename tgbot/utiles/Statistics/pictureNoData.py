from io import BytesIO

from PIL import Image, ImageDraw, ImageFont
import os

from tgbot.utiles.firebaseStorage import download_file_to_RAM


def createPictureNoData(ID, date):

    # Настройки изображения
    width, height = 700, 700
    text_color = (255, 255, 255)  # Белый текст
    font_size = 40

    # Загрузка изображения фона
    file_data = download_file_to_RAM("logo.jpg")
    background_image = Image.open(BytesIO(file_data.read()))
    background_image = background_image.resize((width, height))

    # Создание объекта рисования
    draw = ImageDraw.Draw(background_image)

    # Загрузка шрифта
    # font_path = os.getcwd() + r"\tgbot\utiles\Statistics\Config\FranklinGothicMedium.ttf"
    font_path = download_file_to_RAM("FranklinGothicMedium.ttf")
    font = ImageFont.truetype(BytesIO(font_path.read()), font_size)

    text = f"{date} - Нет данных"

    # Вставка текста на изображение
    x = 130
    y = 100
    draw.text((x, y), text, fill=text_color, font=font)

    # Сохранение изображения с текстом
    result_image = BytesIO()
    background_image.save(result_image, format="JPEG")
    result_image.seek(0)  # Сбрасываем позицию в начало буфера


    # return result_image_path
    return result_image

