from datetime import datetime
from typing import NamedTuple
from parser.types import Asset, Lang, Direction


class Idea(NamedTuple):
    username: str
    likes_count: int
    date: datetime
    # tags: tuple[str]
    directon: Direction
    exchange: str
    ticker: str
    description: str
    # commetns: list[str]


class ParserConfig(NamedTuple):
    lang: Lang
    pages_count: int
    asset: Asset
    batch_size: int = 10
    sleep_duration: int = 1
