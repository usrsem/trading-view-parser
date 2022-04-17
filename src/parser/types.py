from enum import Enum


Asset = str
Html = str


class Lang(Enum):
    EN = "en"
    RU = "ru"
    DE = "de"


class Direction(Enum):
    LONG = 0
    SHORT = 1
    NOT_FOUND = 2

