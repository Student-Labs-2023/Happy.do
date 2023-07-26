import random
from typing import List
from pydantic import BaseModel
import yaml


class Keyboard(BaseModel):
    menu: List[str]
    admin: List[str]
    stat: List[str]


class Choice(BaseModel):
    default: str
    stat: str
    emoji: str
    select_emoji: str


class UserStat(BaseModel):
    day: str
    week: str
    month: str
    all: str


class AdminStatUsers(BaseModel):
    all: str
    new: str


class AdminStat(BaseModel):
    day: str
    week: str
    month: str
    users: AdminStatUsers


class Admin(BaseModel):
    login: str
    exit: str
    stat: AdminStat


class Answer(BaseModel):
    user_stat: UserStat
    admin: Admin


class Exceptions(BaseModel):
    no_data: str


class BotMessages(BaseModel):
    start: str
    choice: Choice
    answer: Answer
    regular: List[str]
    exceptions: Exceptions

    @property
    def get_any_regular(self) -> str:
        """
        Функция get_any_regular возвращает случайную строку из regular.

        :param self: Refer to the object itself
        :return: A random string of regular
        """
        return str(random.choice(self.regular))


class BotContent(BaseModel):

    buttons: List[str]
    keyboard_buttons: Keyboard
    messages: BotMessages

    @property
    def keyboard(self) -> list[str]:
        """
        @property нужен для того, чтобы обозначить,
        что метод 'keyboard' является свойством класса,
        которое можно вызвать без использования скобочек
        """
        return self.buttons

    @classmethod
    def parse_yaml(cls, filepath: str):
        """
        Парсит данные из YAML файла в класс BotContent

        :param filepath: Путь к YAML файлу
        """
        with open(filepath, 'r', encoding='utf-8') as file:
            content = yaml.safe_load(file)

        return cls.model_validate(content)


bot_content = BotContent.parse_yaml('happy.do-bot.content.yaml')
