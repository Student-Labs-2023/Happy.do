from typing import List
from pydantic import BaseModel
import yaml

from config import config


class Keyboard(BaseModel):
    menu: List[str]
    admin: List[str]
    stat: List[str]
    addSmile: List[str]
    premium_list_default: List[str]
    premium_list_state: List[str]


class BotContent(BaseModel):
    buttons: List[str]
    keyboard_buttons: Keyboard

    @classmethod
    def parse_yaml(cls, filepath: str):
        """
        Парсит данные из YAML файла в класс BotContent

        :param filepath: Путь к YAML файлу
        """
        with open(filepath, 'r', encoding='utf-8') as file:
            content = yaml.safe_load(file)

        return cls.model_validate(content)


CONTENT = BotContent.parse_yaml(config.PATH_CONTENT_FILE)
