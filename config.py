from pydantic_settings import BaseSettings
from pydantic import SecretStr

from typing import List


class Settings(BaseSettings):
    BOT_TOKEN: SecretStr
    PAYMENTS_TOKEN: SecretStr
    OPENAI_API_KEY: SecretStr
    FIREBASE_STORAGE_FOLDER_PATH: SecretStr

    WEBHOOK_HOST: str = 'host'
    WEBHOOK_PATH: str = f'/webhook/'

    WEBAPP_HOST: str
    WEBAPP_PORT: int

    PATH_FIREBASE_KEY: str
    PATH_CONTENT_FILE: str

    ADMIN_ID: List[int]

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'


config = Settings()
