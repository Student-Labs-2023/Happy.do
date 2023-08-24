import openai

from config import config

openai.api_key = config.OPENAI_API_KEY.get_secret_value()


async def create_picture_week(prompt: str) -> str:
    """
    Функция create_picture_week генерирует графический портрет за неделю.

    :param prompt: Промпт, по которому создается картинка.
    :return: URL-путь к картинке.
    """
    print(prompt)
    response = await openai.Image.acreate(
        # prompt=f"Create a captivating and high-quality 4K portrait featuring a single human face as the central focus. The portrait should artfully convey the user's emotional journey throughout the past week, based on their selected sequence of smileys {smiles}. Pay meticulous attention to facial features, ensuring lifelike detail and expressions. The subject of the portrait should be distinctly recognizable as either a male or female individual. Enrich the background with carefully chosen visual effects that seamlessly harmonize with the user's emotional states over the specified time period. The end result should be a visually stunning and emotionally resonant piece of art.",
        prompt=f"{prompt}, Color Field Painting, Product-View, Colorful, Rim Lighting",
        n=1,
        size="512x512"
    )
    image_url = response['data'][0]['url']
    return image_url


async def create_picture_day(prompt: str) -> str:
    """
    Функция create_picture_day генерирует графический портрет за день.

    :param prompt: Промпт, по которому создается картинка.
    :return: URL-путь к картинке.
    """
    print(prompt)
    response = await openai.Image.acreate(
        # prompt=f"Craft an exquisite 4K portrait featuring a single, human face at the forefront. This portrait should encapsulate the user's emotions and experiences over the course of a single day, using the sequence of smileys selected {smiles}. Pay meticulous attention to facial details and expressions to ensure a lifelike representation. The individual depicted should be clearly identifiable as either male or female. Elevate the visual impact with a background that integrates tasteful visual effects reflecting the user's emotional journey throughout the day. The final output should be a work of art that not only captures the essence of the user's day but also stands as a testament to the power of visual storytelling.",
        prompt=f"{prompt}, Color Field Painting, Product-View, Colorful, Rim Lighting",
        n=1,
        size="512x512"
    )
    image_url = response['data'][0]['url']
    return image_url
