import openai

from config import config


openai.api_key = config.OPENAI_API_KEY.get_secret_value()


async def create_psychological_portrait(smilesDict: {}) -> str:
    """
    В messages мы можем составить диалог и указать поведение ассистента, на которое он будет ориентироваться
    для последующих своих ответов. Ответ приходит в json формате, откуда далее мы вытаскиваем ответ.

    :return: Возвращает текст сгенерированного сообщения chatGPT.
    """
    smilesStr = '\n'.join('{}: {}'.format(key, val) for key, val in smilesDict.items())  # Словарь в строку

    chat_completion_resp = await openai.ChatCompletion.acreate(
                model="gpt-3.5-turbo",
                messages=[
                {"role": "system", "content": 'Пользователь в течении недели отправлял телеграм-боту смайлики, '
                                              'которые характеризовали его эмоциональное состояние на момент '
                                              'отправки смайлика. Ты получаешь эти смайлики в следующем виде: '
                                              '"(дата): (набор смайликов через запятую)" и затем '
                                              'составляешь довольно развернуто психологический портрет '
                                              'пользователя по его смайликам за неделю. '
                                              'В качестве вывода ты отправляешь '
                                              'пользователю его психологический портрет и по необходимости даёшь ему '
                                              'рекомендации как улучшить свое психологическое здоровье'
                },  # Задаем поведение помощнику
                {"role": "user", "content": f"Составь мой психологический портрет по этим данным. \n{smilesStr}"}  # Задаем вопрос боту
                ]
    )

    return chat_completion_resp.choices[0].message.content