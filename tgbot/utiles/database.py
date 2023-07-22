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


async def createUser(ID, name):
    """ Создание нового пользователя """
    await firestore_client.collection("Users").document(str(ID)).set(
        {"name": name, "status": "default", "notification": "22:00", "registration_date": str(date.today())})
    await firestore_client.collection("Users").document(str(ID)).collection("smile").document("date").set({})


async def checkUser(ID: str) -> bool:
    info = await firestore_client.collection("Users").document(ID).get()
    return info.to_dict() is not None


async def getUsername(ID):
    info = await firestore_client.collection("Users").document(str(ID)).get()
    return info.to_dict()['name']


async def addOrChangeSmile(ID, day, smile):
    if '✅' in smile:
        await firestore_client.collection("Users").document(str(ID)).collection("smile").document("date").update(
            {day: firestore.DELETE_FIELD})
        await addOrRemoveValuesSmileInfo(smile[0], False)
    else:
        await firestore_client.collection("Users").document(str(ID)).collection("smile").document("date").update(
            {day: smile})

        doc_exist = await firestore_client.collection("Smile info").document(str(date.today())).get()
        if doc_exist.exists:
            smile_exist_today = await checkSmileExistToday(smile)
            if smile_exist_today:
                await addOrRemoveValuesSmileInfo(smile, True)
            else:
                await firestore_client.collection("Smile info").document(str(date.today())).update({smile: '1'})
        else:
            await firestore_client.collection("Smile info").document(str(date.today())).set({smile: '1'})


async def checkSmileExistToday(smile):
    '''Проверка ставили ли этот смайлик сегодня'''
    info = await firestore_client.collection("Smile info").document(str(date.today())).get()
    return smile in info.to_dict()


async def addOrRemoveValuesSmileInfo(smile: str, add: bool):
    info = await firestore_client.collection("Smile info").document(str(date.today())).get()
    if add:
        await firestore_client.collection("Smile info").document(str(date.today())).update(
            {smile: str(int(info.to_dict()[smile]) + 1)})
    else:
        if int(info.to_dict()[smile]) == 1:
            await firestore_client.collection("Smile info").document(str(date.today())).update(
                {smile: firestore.DELETE_FIELD})
        else:
            await firestore_client.collection("Smile info").document(str(date.today())).update(
                {smile: str(int(info.to_dict()[smile]) - 1)})


async def delUser(ID):
    await firestore_client.collection("Users").document(str(ID)).delete()


async def getSmileInfo(ID, day):
    info = await firestore_client.collection("Users").document(str(ID)).collection("smile").document("date").get()
    if day == "all":
        return info.to_dict()
    else:
        return info.to_dict()[day]


async def getCountAllUsers() -> int:
    '''Возвращает кол-во всех пользователей'''
    counter = 0
    async for count_users in firestore_client.collection("Users").stream():
        counter += 1
    return counter


async def getCountNewUsers() -> int:
    '''Возвращает кол-во новых пользователей за последнюю неделю'''
    days_range = 7
    base = date.today()
    date_list = [base - timedelta(days=x) for x in range(days_range)]
    counter = 0
    async for count_users in firestore_client.collection("Users").stream():
        if count_users.to_dict()["registration_date"] in (str(week_day) for week_day in date_list):
            counter += 1
    return counter


async def getDictOfStat(days_range: int) -> list:
    base = date.today()
    date_list = [base - timedelta(days=x) for x in range(days_range)]
    result_dicts = []
    async for stat_data in firestore_client.collection("Smile info").stream():
        if stat_data.id in (str(week_day) for week_day in date_list):
            result_dicts.append(dict(stat_data.to_dict()))
    return result_dicts


async def convertDictToStat(dicts: list) -> dict:
    from collections import defaultdict
    sum_dict = defaultdict(int)
    for d in dicts:
        for emoji, value in d.items():
            sum_dict[emoji] += int(value)
    final_dict = dict(sum_dict)
    return final_dict


async def getStatAdmin(days_range: int) -> list:
    '''Статистика за дни'''
    stat_dict = await getDictOfStat(days_range)
    emoji_dict = await convertDictToStat(stat_dict)
    emoji_dict = [f"{emoji} : {value}" for emoji, value in emoji_dict.items()]
    return emoji_dict
