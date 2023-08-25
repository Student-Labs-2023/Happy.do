import openai

from config import config


openai.api_key = config.OPENAI_API_KEY.get_secret_value()


async def create_psychological_portrait_week(smilesWeek: str) -> str:
    """
    Генерирует психологический портрет за неделю.

    В messages мы можем составить диалог и указать поведение ассистента, на которое он будет ориентироваться
    для последующих своих ответов. Ответ приходит в json формате, откуда далее мы вытаскиваем ответ.

    :return: Возвращает текст сгенерированного сообщения chatGPT.
    """
    # smilesStr = '\n'.join('{}: {}'.format(key, val) for key, val in smilesDict.items())  # Словарь в строку

    chat_completion_resp = await openai.ChatCompletion.acreate(
                model="gpt-3.5-turbo",
                messages=[
                {"role": "system", "content": 'Пользователь в течении недели отправлял телеграм-боту смайлики, '
                                              'которые характеризовали его эмоциональное состояние на момент '
                                              'отправки смайлика. Ты получаешь эти смайлики в следующем виде: '
                                              '"(Количество дней до сегодняшней даты): (набор смайликов через запятую)" и затем '
                                              'В качестве вывода ты отправляешь ему'
                                              'рекомендации как улучшить свое психологическое здоровье, очень ёмко и содержательно '
                                              'Сообщение начинаешь со слов: "Привет! Я проанализировал все смайлики, '
                                              'которые ты отправлял за последние 7 дней". '
                                              'Общайся с пользователем как с другом. Твоё сообщение должно быть буквально '
                                              'не больше 7 предложений. Твоё сообщение должно быть очень ёмким!'
                },  # Задаем поведение помощнику
                {"role": "user", "content": f"Дай мне рекомендации по этим данным. \n{smilesWeek}"}  # Задаем вопрос боту
                ],
                max_tokens=700
    )

    return chat_completion_resp.choices[0].message.content


async def create_psychological_portrait_day(smilesDay: str) -> str:
    """
    Генерирует рекомендации за день.

    :param smilesDay: Смайлики выбранные за день в строковом формате.
    :return: Возвращает текст сгенерированного сообщения chatGPT.
    """

    chat_completion_resp = await openai.ChatCompletion.acreate(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": 'Пользователь в течении дня отправлял телеграм-боту смайлики, '
                                          'которые характеризовали его эмоциональное состояние на момент '
                                          'отправки смайлика. Ты получаешь эти смайлики  '
                                          'одной строкой через запятую и затем '
                                          'составляешь довольно ёмко психологический портрет '
                                          'пользователя по его смайликам за день. '
                                          'В качестве вывода ты отправляешь ему'
                                          'рекомендации как улучшить свое психологическое здоровье, очень ёмко и содержательно '
                                          'Сообщение начинаешь со слов: "Привет! Я проанализировал все смайлики, '
                                          'которые ты отправлял в течении этого дня". '
                                          'Общайся с пользователем как с другом. Твоё сообщение должно быть буквально '
                                          'не больше 7 предложений. Твоё сообщение должно быть очень ёмким!'
             },  # Задаем поведение помощнику
            {"role": "user", "content": f"Дай мне рекомендации по этим данным. \n{smilesDay}"}
            # Задаем вопрос боту
        ],
        max_tokens=700
    )

    return chat_completion_resp.choices[0].message.content


async def generation_prompt(smiles: str, period: str) -> str:
    """
    Функция generation_prompt используется для создания промпта для DALL-E.

    :param smiles: Смайлики пользователя.
    :param period: Период за который генерируется портрет.
    :return: Промпт.
    """

    chat_completion_resp = await openai.ChatCompletion.acreate(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": f'Пользователь в течении {"дня" if period == "day" else "недели"} '
                                          f'отправлял телеграм-боту смайлики, '
                                          'которые характеризовали его эмоциональное состояние на момент '
                                          'отправки смайлика. Описание должно быть одним предложением на все смайлики '
                                          'сразу. Использовать эти смайлики в ответе нельзя. Без переходов, это должно '
                                          'быть описанием одного лица. В ответе не должно быть запятых и любых другиз '
                                          'знаков препинания. Проанализируй смайлики и выдели на лице только те, '
                                          'которые преобладают над другими.'
             },  # Задаем поведение помощнику
            {"role": "user", "content": f'Make a description of the face using these emoticons:'
                                        f'😴, 😪, 🥱, 😍, 😡'},
            # {"role": "assistant", "content": f'The face expresses fatigue, drowsiness, loneliness and irritation, '
            #                                  f'while showing displeasure and attraction to something pleasant.'},
            {"role": "assistant", "content": f'Very tired and sleepy face'},
             {"role": "user", "content": f"Make a description of the face using these emoticons:"
                                        f"\n{smiles}"}
            # Задаем вопрос боту
        ],
        max_tokens=700

    )
    print(chat_completion_resp.choices[0].message.content)

    return chat_completion_resp.choices[0].message.content