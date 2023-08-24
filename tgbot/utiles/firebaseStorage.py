from io import BytesIO

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


def download_file_to_local(storage_path: str, local_path: str) -> None:
    """
    Функция download_file используется для загрузки файла из Firebase storage на диск.

    :param storage_path: Путь к файлу в хранилище.
    :param local_path: Локальный путь к файлу.
    """
    blob = bucket.blob(storage_path)
    blob.download_to_filename(local_path)


def download_file_to_RAM(storage_path: str) -> BytesIO:
    """
    Функция download_file используется для загрузки файла из Firebase storage в оперативную память.

    :param storage_path: Путь к файлу в хранилище.
    :return: Файл с картинкой.
    """
    blob = bucket.blob(storage_path)
    file_data = blob.download_as_bytes()

    return BytesIO(file_data)
