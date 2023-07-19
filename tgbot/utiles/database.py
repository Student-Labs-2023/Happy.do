import json

from google.cloud.firestore import AsyncClient
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
        {"name": name, "status": "default", "notification": "22:00"})
    await firestore_client.collection("Users").document(str(ID)).collection("smile").document("date").set({})
    # await firestore_client.collection("Users").document(str(ID)).collection("smile").document("week").set(
    #     {"Monday": "", "Tuesday": "", "Wednesday": "", "Thursday": "", "Friday": "", "Saturday": "", "Sunday": ""})


async def checkUser(ID: str) -> bool:
    info = await firestore_client.collection("Users").document(ID).get()
    return info.to_dict() is not None


async def getUsername(ID):
    info = await firestore_client.collection("Users").document(str(ID)).get()
    return info.to_dict()['name']


async def addOrChangeSmile(ID, day, smile):
    # info = firestore_client.collection("Users").document(str(ID)).collection("smile").document("date")
    # if info.get()[day] is not None :
    # await info.update({day: smile})
    await firestore_client.collection("Users").document(str(ID)).collection("smile").document("date").update(
        {day: smile})
    # try:
    #     await info.set({day: smile})
    # except Exception: # проверить название ошибки
    #     await info.update({day: smile})


async def delUser(ID):
    await firestore_client.collection("Users").document(str(ID)).delete()


async def getSmileInfo(ID, day):
    info = await firestore_client.collection("Users").document(str(ID)).collection("smile").document("date").get()
    if day == "all":
        return info.to_dict()
    else:
        return info.to_dict()[day]
