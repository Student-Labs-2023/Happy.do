import json
from datetime import date, timedelta

from google.cloud.firestore import AsyncClient
from google.cloud import firestore
from google.oauth2 import service_account

from config import config

with open(fr"{config.PATH_FIREBASE_KEY}") as json_file:
    json_data = json.load(json_file)

firestore_client = AsyncClient(
    project=json_data['project_id'],
    credentials=service_account.Credentials.from_service_account_info(json_data),
)


async def createUser(ID: int, name: str) -> None:
    """
    Функция createUser используется для создания нового пользователя в БД.

    :param ID: Telegram user ID
    :param name: Telegram user name
    """
    await firestore_client.collection("Users").document(str(ID)).set(
        {"name": name, "status": "default", "notification": "22:00", "registration_date": str(date.today()),
         "smile_used": 0, "personal_smiles": None})
    await firestore_client.collection("Users").document(str(ID)).collection("smile").document("date").set({})


async def addEmojiUsed(ID: int) -> None:
    """
    Функция addEmojiUsed используется для добавления к полю smile_used 1 значения.

    :param ID: Telegram user ID
    """
    await firestore_client.collection("Users").document(str(ID)).update({"smile_used": firestore.Increment(1)})


async def addPersonalSmiles(ID: int, smile: str):
    """
    Функция addPersonalSmiles используется для добавления персональных смайликов в базу данных.

    :param ID: Telegram user ID
    :param smile: Смайлик, который передается в базу
    """
    smiles = await getPersonalSmiles(ID)
    smiles.append(smile)

    await firestore_client.collection("Users").document(str(ID)).update(
        {"personal_smiles": smiles[0] if len(smiles) == 1 else ", ".join(smiles)})


async def emojiLimitExpired(ID: int) -> bool:
    """
    Функция emojiLimitExpired используется для проверки, использовал ли пользователь 100 смайликов,
    если да возвращает True, иначе False.

    :param ID: Telegram user ID
    :return: Если использований >= 100 возвращает True, иначе False.
    """
    info = await firestore_client.collection("Users").document(str(ID)).get()
    if info.to_dict()["smile_used"] >= 100:
        return True
    return False


async def checkUser(ID: int) -> bool:
    """
    Функция checkUser используется для проверки, существует ли пользователь в БД, если да возвращает True, иначе False.

    :param ID: Telegram user ID
    :return: Если существует True, иначе False
    """
    info = await firestore_client.collection("Users").document(str(ID)).get()
    return info.to_dict() is not None


async def getUsername(ID: int) -> str:
    """
    Функция getUsername возвращает имя пользователя в формате str по его id.

    :param ID: Telegram user ID
    :return: Имя пользователя в формате str по его id
    """
    info = await firestore_client.collection("Users").document(str(ID)).get()
    return info.to_dict()['name']


async def addOrChangeSmile(ID: int, day: str, smilesList: []) -> None:
    """
    Функция addOrChangeSmile используется для добавления или изменения 'smile' в базе данных.

    Если в 'smile' существует '✅', тогда в документе 'ID', коллекции 'smile', в документе 'date' удаляется поле
    сегодняшнего дня.

    Иначе это поле перезаписывается строкой 'smile'.

    :param ID: Telegram user ID
    :param day: The date the function was called
    :param smile: The content of the pressed button
    """

    smiles = ", ".join(smilesList)

    if len(smilesList):
        await firestore_client.collection("Users").document(str(ID)).collection("smile").document(
            "date").update({day: smiles})
    else:
        await firestore_client.collection("Users").document(str(ID)).collection("smile").document(
            "date").update({day: firestore.DELETE_FIELD})


    # Переделать админку под новую возможность отправлять несколько смайликов за раз
        # await addOrRemoveValuesSmileInfo(smile[0], False)


    # if '✅' in smile:
    #     await firestore_client.collection("Users").document(str(ID)).collection("smile").document(str(date.today())).update(
    #         {"smile": firestore.DELETE_FIELD})
    #     await addOrRemoveValuesSmileInfo(smile[0], False)
    # else:
    #     await firestore_client.collection("Users").document(str(ID)).collection("smile").document("date").update(
    #         {day: smile})

        # doc_exist = await firestore_client.collection("Smile info").document(str(date.today())).get()
        # if doc_exist.exists:
        #     smile_exist_today = await checkSmileExistToday(smiles)
        #     if smile_exist_today:
        #         await addOrRemoveValuesSmileInfo(smiles, True)
        #     else:
        #         await firestore_client.collection("Smile info").document(str(date.today())).update({smiles: '1'})
        # else:
        #     await firestore_client.collection("Smile info").document(str(date.today())).set({smiles: '1'})


async def checkSmileExistToday(smile) -> bool:
    """
    Функция checkSmileExistToday используется для проверки ставился ли "smile" сегодня.

    :param smile: Строка со смайлом
    :return: Если ставился - True, иначе False
    """
    info = await firestore_client.collection("Smile info").document(str(date.today())).get()
    return smile in info.to_dict()


async def addOrRemoveValuesSmileInfo(smilesList: [], add: bool) -> None:
    """
    Функция addOrRemoveValuesSmileInfo используется для добавления или удаления смайла из коллекции "Smile info",
    документа сегодняшнего дня.

    :param smile: Строка со смайлом
    :param add: Параметр типа bool, если True, то будет добавлен смайл, иначе будет удален
    """

    # Переделать под новый ввод большего числа смайликов
    for smile in smilesList: # возможно нужно добавить async
        info = await firestore_client.collection("Smile info").document(str(date.today())).get()
        if add:
            await firestore_client.collection("Smile info").document(str(date.today())).update(
                {smile: str(int(info.to_dict()[smile]) + 1)})
        else:
            # Сделать нормальное удаление прошлого значения, не всего поля, а одного значения
            if int(info.to_dict()[smile]) == 1:
                await firestore_client.collection("Smile info").document(str(date.today())).update(
                    {smile: firestore.DELETE_FIELD})
            else:
                await firestore_client.collection("Smile info").document(str(date.today())).update(
                    {smile: str(int(info.to_dict()[smile]) - 1)})


async def delUser(ID: int) -> None:
    """
    Функция delUser используется для удаления пользователя из базы данных по его Telegram user ID.

    :param ID: Telegram user ID
    """
    await firestore_client.collection("Users").document(str(ID)).delete()


async def getSmileInfo(ID: int, day: str):
    """
    Функция getSmileInfo используется для получения информации по проставленным смайликам.

    При day == "all" возвращается словарь со всеми данными.
    При другом значении day возвращается список со смайликами за какойто конкретный день.

    :param ID: Telegram user ID
    :param day: Дата, по какому дню требуется информация
    :return: Словарь с информацией о смайликах за day
    """

    info = await firestore_client.collection("Users").document(str(ID)).collection("smile").document("date").get()
    if day == "all":
        smiles = dict(sorted(info.to_dict().items()))
        return smiles
    else:
        _ = info.to_dict()[day]
        return list(_) if ", " not in _ else _.split(", ")  # Возвращает список смайликов за день


async def getCountAllUsers() -> int:
    """
    Функция getCountAllUsers используется для получения количества всех зарегистрированных пользователей.

    :return: Значение типа int, кол-во всех пользователей
    """
    counter = 0
    async for count_users in firestore_client.collection("Users").stream():
        counter += 1
    return counter


async def getPersonalSmiles(ID: int):
    """
    Функция getPersonalSmiles используется для получения персональных смайликов.

    :param ID: Telegram user ID
    :return: Список персональных смайликов
    """
    info = await firestore_client.collection("Users").document(str(ID)).get()
    _ = info.to_dict()["personal_smiles"]
    return list(_) if ", " not in _ else _.split(", ")


async def getCountNewUsers() -> int:
    """
    Функция getCountNewUsers используется для получения количества всех пользователей, которые зарегистрировались
    за последнюю неделю.

    :return: Значение типа int, кол-во новых пользователей
    """

    days_range = 7
    base = date.today()
    date_list = [base - timedelta(days=x) for x in range(days_range)]
    counter = 0
    async for count_users in firestore_client.collection("Users").stream():
        if count_users.to_dict()["registration_date"] in (str(week_day) for week_day in date_list):
            counter += 1
    return counter


async def getDictOfStat(days_range: int) -> list:
    """
    Функция getDictOfStat используется для получения списка из словарей с информацией о проставленных смайликах
    за указанный период days_range.

    :param days_range: Значение типа int, период необходимой статистики в днях
    :return: Список из словарей с информацией о проставленных смайликах
    """

    base = date.today()
    date_list = [base - timedelta(days=x) for x in range(days_range)]
    result_dicts = []
    async for stat_data in firestore_client.collection("Smile info").stream():
        if stat_data.id in (str(week_day) for week_day in date_list):
            result_dicts.append(dict(stat_data.to_dict()))
    return result_dicts


async def convertDictToStat(dicts: list) -> dict:
    """
    Функция convertDictToStat используется для преобразования списка из словарей в один список,
    при это складывая все повторяющиеся значения смайликов в этих словарях.

    :param dicts: Список из словарей из функции getDictOfStat
    :return: Словарь общей статистики, составленный из списка dicts
    """

    from collections import defaultdict
    sum_dict = defaultdict(int)
    for d in dicts:
        for emoji, value in d.items():
            sum_dict[emoji] += int(value)
    final_dict = dict(sum_dict)
    return final_dict


async def getStatAdmin(days_range: int) -> list:
    """
    Функция getStatAdmin используется для получения общей статистики проставления смайликов за заданный период времени.

    :param days_range: Значение типа int, период необходимой статистики в днях
    :return: Список отформатированной статистики
    """

    stat_dict = await getDictOfStat(days_range)
    emoji_dict = await convertDictToStat(stat_dict)
    emoji_dict = [f"{emoji} : {value}" for emoji, value in emoji_dict.items()]
    return emoji_dict
