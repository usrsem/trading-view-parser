from enum import Enum


Asset = str
Html = str


class Lang(Enum):
    EN = "en"
    RU = "ru"
    DE = "de"


class Direction(Enum):
    LONG = "long"
    SHORT = "short"
    NOT_FOUND = "empty"

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.__str__()

