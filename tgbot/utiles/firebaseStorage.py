from io import BytesIO
from uuid import uuid4

import firebase_admin
from firebase_admin import credentials, storage

from config import config

cred = credentials.Certificate(config.PATH_FIREBASE_KEY)
firebase_admin.initialize_app(cred, {
    'storageBucket': config.FIREBASE_STORAGE_FOLDER_PATH.get_secret_value()
})

bucket = storage.bucket()


def upload_file(local_path: str, storage_path: str) -> None:
    """
    Функция upload_file используется для загрузки файла в Firebase storage.

    :param local_path: Локальный путь к файлу.
    :param storage_path: Путь к файлу в хранилище.
    """
    blob = bucket.blob(storage_path)
    blob.upload_from_filename(local_path)
    print(f"File {local_path} uploaded to {storage_path}")


# def upload_public_file(file: BytesIO) -> str:
#     """
#     Функция upload_public_file используется для загрузки файла,
#     сохраненного в оперативной памяти, в Firebase storage.
#
#     :param file: Файл, сохраненный в оперативной памяти.
#     :return: URL с расположением файла в базе.
#     """
#     print("START LOAD IMAGE")
#     blob = bucket.blob(str(uuid4()) + ".jpg")
#     blob.upload_from_file(file)
#     blob.make_public()
#     url = blob.public_url
#     index = url.rfind("/") + 1
#     url = url[index:]
#     print("your file url", url)
#     return url


def download_file_to_local(storage_path: str, local_path: str) -> None:
    """
    Функция download_file используется для загрузки файла из Firebase storage на диск.

    :param storage_path: Путь к файлу в хранилище.
    :param local_path: Локальный путь к файлу.
    """
    blob = bucket.blob(storage_path)
    blob.download_to_filename(local_path)
    print(f"File {storage_path} downloaded to {local_path}")


def download_file_to_RAM(storage_path: str) -> BytesIO:
    """
    Функция download_file используется для загрузки файла из Firebase storage в оперативную память.

    :param storage_path: Путь к файлу в хранилище.
    :return: Файл с картинкой.
    """
    blob = bucket.blob(storage_path)
    file_data = blob.download_as_bytes()

    return BytesIO(file_data)
