from typing import NamedTuple
from enum import Enum


Asset = str


class Lang(Enum):
    EN = "en"
    RU = "ru"
    DE = "de"


class ParserConfig(NamedTuple):
    lang: Lang
    pages_count: int
    asset: Asset

