import json
import hashlib, base64

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
         "smile_used": 0, "personal_smiles": "", "used_GPT": 0, "used_GPT_date": None,
         "date_registration_premium": "undefined",
         "premium_status_end": "undefined", "prev_invoice_msg_id": None, "prev_smile_msg_id": None, "state": None})
    await firestore_client.collection("Users").document(str(ID)).collection("smile").document("date").set({})
    await firestore_client.collection("Users").document(str(ID)).collection("states").document("message_id").set({
        "stat_day": None, "stat_week": None, "stat_month": None, "stat_alltime": None})


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


async def removePersonalSmile(ID: int, smile: str):
    """
    Функция removePersonalSmile используется для удаления персональных смайликов из базы данных.

    :param ID: Telegram user ID
    :param smile: Смайлик, который удаляется из базы
    """
    smiles = await getPersonalSmiles(ID)

    smiles.remove(smile)
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
    :param smilesList: Smiles list
    """

    smiles = ", ".join(smilesList)
    pastSmilesList = await firestore_client.collection("Users").document(str(ID)).collection("smile").document(
        "date").get()
    try:
        pastSmilesList = pastSmilesList.to_dict()[str(date.today())]
    except KeyError:
        pastSmilesList = {}

    if len(smilesList):
        await addOrRemoveValuesSmileInfo(smilesList, pastSmilesList)
        await firestore_client.collection("Users").document(str(ID)).collection("smile").document(
            "date").update({day: smiles})
    else:
        await addOrRemoveValuesSmileInfo(smilesList, pastSmilesList)
        await firestore_client.collection("Users").document(str(ID)).collection("smile").document(
            "date").update({day: firestore.DELETE_FIELD})


async def checkSmileExistToday(smile) -> bool:
    """
    Функция checkSmileExistToday используется для проверки ставился ли "smile" сегодня.

    :param smile: Строка со смайлом
    :return: Если ставился - True, иначе False
    """
    info = await firestore_client.collection("Smile info").document(str(date.today())).get()
    return smile in info.to_dict()


async def getSmileInfoToday():
    """
    Функция getSmileInfoToday используется для получения общей статистики за сегодня.
    """

    async for stat_data in firestore_client.collection("Smile info").stream():
        if stat_data.id == str(date.today()):
            info = await firestore_client.collection("Smile info").document(str(date.today())).get()
            return info
    return {}


async def addOrRemoveValuesSmileInfo(smilesList: [], pastSmilesList: []) -> None:
    """
    Функция addOrRemoveValuesSmileInfo используется для добавления или удаления смайла из коллекции "Smile info",
    документа сегодняшнего дня.

    :param smilesList: Список со смайлом
    :param pastSmilesList: Прошлый список со смайликами, если имеется
    """

    info = await getSmileInfoToday()
    if info == {}:
        for smile in smilesList:
            await firestore_client.collection("Smile info").document(str(date.today())).set({smile: 1})
    else:
        newSmileListAdd = list(set(smilesList) - set(pastSmilesList))
        newSmileListRemove = list(set(pastSmilesList) - set(smilesList))
        newDict = info.to_dict()
        if newSmileListAdd:
            for smile in newSmileListAdd:
                if smile in newDict:
                    newDict[smile] += 1
                else:
                    newDict[smile] = 1
            await firestore_client.collection("Smile info").document(str(date.today())).set(newDict)
        else:
            for smile in newSmileListRemove:
                if smile in newDict:
                    if newDict[smile] == 1:
                        del newDict[smile]
                    else:
                        newDict[smile] -= 1
            await firestore_client.collection("Smile info").document(str(date.today())).set(newDict)

    # if add:
    #     if not pastSmilesList:

    # Переделать под новый ввод большего числа смайликов
    # for smile in smilesList: # возможно нужно добавить async
    #     info = await firestore_client.collection("Smile info").document(str(date.today())).get()
    #     if add:
    #         await firestore_client.collection("Smile info").document(str(date.today())).update(
    #             {smile: str(int(info.to_dict()[smile]) + 1)})
    #     else:
    #         # Сделать нормальное удаление прошлого значения, не всего поля, а одного значения
    #         if int(info.to_dict()[smile]) == 1:
    #             await firestore_client.collection("Smile info").document(str(date.today())).update(
    #                 {smile: firestore.DELETE_FIELD})
    #         else:
    #             await firestore_client.collection("Smile info").document(str(date.today())).update(
    #                 {smile: str(int(info.to_dict()[smile]) - 1)})


async def addPortrait(body: str, text: str, period: str) -> None:
    """
    Функция addPortrait используется для добавления сгенерированноого портрета в базу данных.

    :param body: Последовательность смайликов.
    :param text: Сгенерированный портрет.
    :param period: Период, за который должен генерироваться портрет.
    """

    key = base64.b16encode(hashlib.sha256(body.encode('utf-8')).digest()).decode("utf-8")

    await firestore_client.collection("Portraits").document(period).update({key: text})


async def getExistingPortrait(body: str, period: str) -> str:
    """
    Функция getExistingPortrait используется для проверки и получения имеющегося портрета в базе по определенной
    последовательности смайликов.

    :param body: Последовательность смайликов.
    :param period: Период, за который должен генерироваться портрет.
    :return: Если находит портрет, то возвращает его, иначе возвращает строку "NotExist".
    """

    key = base64.b16encode(hashlib.sha256(body.encode('utf-8')).digest()).decode("utf-8")

    info = await firestore_client.collection("Portraits").document(period).get()

    try:
        return info.to_dict()[key]
    except KeyError:
        return "NotExist"


async def addUsedGPT(ID: int) -> None:
    """
    Функция addUsedGPT используется для увеличения числа использований chatGPT.
    При вызове этой функции в базе увеличивается количество использований chatGPT на 1.

    :param ID: Telegram user ID
    """

    await firestore_client.collection("Users").document(str(ID)).update({"used_GPT": firestore.Increment(1)})


async def getUsedGPT(ID: int) -> int:
    """
    Функция getUsedGPT используется для получения информации о количестве использований chatGPT.
    При вызове этой функции в базе увеличивается количество использований chatGPT на 1.
    Каждый новый день количество использований обнуляется.

    :param ID: Telegram user ID
    :return: Количество использований chatGPT
    """
    info = await firestore_client.collection("Users").document(str(ID)).get()

    if info.to_dict()["used_GPT_date"] != str(date.today()):
        await firestore_client.collection("Users").document(str(ID)).update({"used_GPT_date": str(date.today()),
                                                                             "used_GPT": 0})
        return 0
    else:
        return info.to_dict()["used_GPT"]


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
    При другом значении day возвращается список со смайликами за какой-то конкретный день.

    :param ID: Telegram user ID
    :param day: Дата, по какому дню требуется информация
    :return: Словарь с информацией о смайликах за day
    """

    info = await firestore_client.collection("Users").document(str(ID)).collection("smile").document("date").get()
    if day == "all":
        smiles = dict(sorted(info.to_dict().items()))
        return smiles
    else:
        try:
            _ = info.to_dict()[day]
            return list(_) if ", " not in _ else _.split(", ")  # Возвращает список смайликов за день
        except KeyError:
            return []


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


async def premiumStatus(ID: int, period: str) -> None:
    """
    Функция premiumStatus используется для изменения статуса пользователя после покупки премиума в БД.

    :param period: Дата окончания подписки
    :param ID: Telegram user ID
    """

    await firestore_client.collection("Users").document(str(ID)).update({"status": "premium",
                                                                         "date_registration_premium": str(date.today()),
                                                                         "premium_status_end": period})


async def checkPremiumUser(ID: int) -> bool:
    """
    Функция checkPremiumUser используется для проверки, есть ли у юзера премиум, возвращает True, если да, иначе False.

    :param ID: Telegram user ID
    """

    info = await firestore_client.collection("Users").document(str(ID)).get()
    info = info.to_dict()["status"]
    if info == "premium":
        return True
    else:
        return False


async def infoPremiumUser(ID: int) -> str:
    """
    Функция infoPremiumUser используется для получения информации до какого числа активен премиум статус.

    :param ID: Telegram user ID
    """

    info = await firestore_client.collection("Users").document(str(ID)).get()
    Date = info.to_dict()["premium_status_end"]
    return f"У вас активен премиум статус до {Date}"


async def updateInvoiceMsgID(ID: int, msg_id: int) -> None:
    """
    Функция updateInvoiceMsgID используется для обновления поля 'prev_invoice_msg_id' значением msg_id.

    :param ID: Telegram user ID
    :param msg_id: Telegram message ID
    """

    await firestore_client.collection("Users").document(str(ID)).update({"prev_invoice_msg_id": msg_id})


async def updateSmileMsgID(ID: int, msg_id: int) -> None:
    """
    Функция updateSmileMsgID используется для обновления поля 'prev_smile_msg_id' значением msg_id.

    :param ID: Telegram user ID
    :param msg_id: Telegram message ID
    """

    await firestore_client.collection("Users").document(str(ID)).update({"prev_smile_msg_id": msg_id})


async def getPrevInvoiceMsgID(ID: int) -> int | None:
    """
    Функция getInvoiceMsgID используется для получения ID последнего сообщения с invoice'ом.

    :param ID: Telegram user ID
    """

    info = await firestore_client.collection("Users").document(str(ID)).get()
    info = info.to_dict()["prev_invoice_msg_id"]
    return info


async def getPrevSmileMsgID(ID: int) -> int | None:
    """
    Функция getSmileMsgID используется для получения ID последнего сообщения со смайликами.

    :param ID: Telegram user ID
    """

    info = await firestore_client.collection("Users").document(str(ID)).get()
    info = info.to_dict()["prev_smile_msg_id"]
    return info


async def getUsersState() -> dict | None:
    """
    Функция getUserState используется для получения state пользователей.

    """

    StateDict = {}
    async for user_data in firestore_client.collection("Users").stream():
        user_state = user_data.to_dict()["state"]
        if user_state is not None:
            StateDict[user_data.id] = user_state
    if StateDict == {}:
        return None
    print(StateDict)
    return StateDict


async def setUserState(ID: int, state: str):
    """
    Функция setUserState используется для обновления поля 'state'.

    :param ID: Telegram user ID
    :param state: Состояние пользователя
    :return:
    """
    await firestore_client.collection("Users").document(str(ID)).update({"state": state})


async def getMessageId(ID: int, message: str) -> int:
    """
    Функция getMessageId используется для получения id сообщения.

    :param ID: Telegram user ID..
    :param message: Наименование сообщения.

    :return: Id сообщения.
    """
    info = await firestore_client.collection("Users").document(str(ID)).collection("states").document("message_id").get()
    if message in info.to_dict():
        info = info.to_dict()[message]
    else:
        await firestore_client.collection("Users").document(str(ID)).collection("states").document("message_id").update(
            {message: None})
        info = None

    return info


async def addMessageId(ID: int, message: str, message_id: int) -> None:
    """
    Функция addMessageId используется для добавления id сообщения в БД.

    :param ID: Telegram user ID..
    :param message: Наименование сообщения.
    :param message_id: Id сообщения.
    """

    info = await firestore_client.collection("Users").document(str(ID)).collection("states").document(
        "message_id").update({message: message_id})

