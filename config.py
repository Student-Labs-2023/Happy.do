from pydantic_settings import BaseSettings
from pydantic import SecretStr


class Settings(BaseSettings):
    BOT_TOKEN: SecretStr
    PAYMENTS_TOKEN: SecretStr
    WEBHOOK_HOST: str = 'host'
    WEBHOOK_PATH: str = f'/webhook/'

    WEBAPP_HOST: str
    WEBAPP_PORT: int

    PATH_FIREBASE_KEY: str
    PATH_CONTENT_FILE: str

    ADMIN_ID: int
    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'


config = Settings()
