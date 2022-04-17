import time

from aiohttp import ClientSession
from asyncio import create_task, gather, sleep
from asyncio.tasks import Task
from parser.config import base_page_url, base_ideas_url, domain
from parser.types import Lang, Html
from parser.models import Idea, ParserConfig
from parser.parse_funcs import parse_cards, get_card_links
from loguru import logger as log
from typing import Generator


def page_link_generator(lang: Lang, page_num: int) -> str:
    page: str = "" if page_num == 1 else f"page-{page_num}/"
    return base_page_url.format(lang=lang.value, page=page)


class TradingParserException(Exception): pass


class TradingViewScraper:
    def __init__(self, config: ParserConfig) -> None:
        self.config: ParserConfig = config
        self.ideas: list[Idea] = []

    async def load_ideas(self) -> None:
        log.info("Starting parsing")
        page_nums: Generator[int, None, None] = self.page_num_generator()
        start = time.monotonic()

        async with ClientSession() as session:
            for batch_size in self.batches_iterator():
                tasks: list[Task] = [
                    create_task(self.get_cards(session, next(page_nums)))
                    for _ in range(batch_size)
                ]

                for cards in await gather(*tasks):
                    self.ideas.extend(parse_cards(cards))
    
                await sleep(self.config.sleep_duration)

        log.info(f"Time passed {int((time.monotonic() - start) // 60)} min")
        log.info(f"Loaded {len(self.ideas)} ideas")


    def page_num_generator(self) -> Generator[int, None, None]:
        for page_num in range(self.config.pages_count):
            yield page_num + 1

    def batches_iterator(self) -> tuple[int, ...]:
        if self.config.batch_size > self.config.pages_count:
            return tuple([self.config.pages_count])

        res = [
            self.config.batch_size
            for _ in range(self.config.pages_count // self.config.batch_size)
        ]

        if (remainder := self.config.pages_count % self.config.batch_size) > 0:
            res.append(remainder)

        return tuple(res)

    async def get_cards(
        self,
        session: ClientSession,
        page_num: int
    ) -> tuple[Html, ...]:
        page_url: str = self.ideas_link_generator(page_num)

        page: Html = await self.load_url(session, page_url)
        links: list[str] = get_card_links(page)
        base_url: str = domain.format(lang=self.config.lang.value)

        tasks: list[Task] = [
            create_task(self.load_url(session, base_url + link))
            for link in links
        ]

        return await gather(*tasks)


    async def load_url(self, session: ClientSession, url: str) -> Html:
        async with session.get(url) as r:
            return await r.text()


    def ideas_link_generator(self, page_num: int) -> str:
        page: str = "" if page_num == 1 else f"page-{page_num}/"
        return base_ideas_url.format(
            lang=self.config.lang.value, asset=self.config.asset.lower(), page=page)

