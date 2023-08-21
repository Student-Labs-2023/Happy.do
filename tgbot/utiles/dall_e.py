import openai

from config import config

openai.api_key = config.OPENAI_API_KEY.get_secret_value()


async def create_picture_week(smiles: str) -> str:
    print(smiles)
    response = await openai.Image.acreate(
        prompt=f"Create a captivating and high-quality 4K portrait featuring a single human face as the central focus. The portrait should artfully convey the user's emotional journey throughout the past week, based on their selected sequence of smileys {smiles}. Pay meticulous attention to facial features, ensuring lifelike detail and expressions. The subject of the portrait should be distinctly recognizable as either a male or female individual. Enrich the background with carefully chosen visual effects that seamlessly harmonize with the user's emotional states over the specified time period. The end result should be a visually stunning and emotionally resonant piece of art.",
        n=1,
        size="512x512"
    )
    image_url = response['data'][0]['url']
    return image_url


async def create_picture_day(smiles: str) -> str:
    print(smiles)
    response = await openai.Image.acreate(
        prompt=f"Craft an exquisite 4K portrait featuring a single, human face at the forefront. This portrait should encapsulate the user's emotions and experiences over the course of a single day, using the sequence of smileys selected {smiles}. Pay meticulous attention to facial details and expressions to ensure a lifelike representation. The individual depicted should be clearly identifiable as either male or female. Elevate the visual impact with a background that integrates tasteful visual effects reflecting the user's emotional journey throughout the day. The final output should be a work of art that not only captures the essence of the user's day but also stands as a testament to the power of visual storytelling.",
        n=1,
        size="512x512"
    )
    image_url = response['data'][0]['url']
    return image_url
