import time

from aiohttp import ClientSession
from asyncio import create_task, gather, sleep
from asyncio.tasks import Task
from parser.config import base_ideas_url, domain
from parser.types import Html
from parser.models import Idea, ParserConfig
from parser.parse_funcs import parse_card, get_card_links
from parser.IdeasSaver import IdeasSaver
from loguru import logger as log
from typing import Generator, Optional


class TradingParserException(Exception): pass


class TradingViewScraper:
    def __init__(self, config: ParserConfig) -> None:
        self.config: ParserConfig = config
        self.ideas: list[Idea] = []
        self.saver: IdeasSaver = IdeasSaver()


    async def start(self) -> None:
        await self._load_ideas()
        self.saver.save2csv(self.ideas)


    async def _load_ideas(self) -> None:
        log.info("Starting parsing")
        page_nums: Generator[int, None, None] = self._page_num_generator()
        start = time.monotonic()

        async with ClientSession() as session:
            for batch_size in self._batches_iterator():
                tasks: list[Task] = [
                    create_task(self._process_page(session, next(page_nums)))
                    for _ in range(batch_size)
                ]

                await gather(*tasks)
                await sleep(self.config.sleep_duration)
                log.info(f"Parsed {batch_size} pages")

        log.info(f"Time passed {int((time.monotonic() - start) // 60)} min")
        log.info(f"Loaded {len(self.ideas)} ideas")


    def _page_num_generator(self) -> Generator[int, None, None]:
        for page_num in range(self.config.pages_count):
            yield page_num + 1

    def _batches_iterator(self) -> tuple[int, ...]:
        if self.config.batch_size > self.config.pages_count:
            return tuple([self.config.pages_count])

        res = [
            self.config.batch_size
            for _ in range(self.config.pages_count // self.config.batch_size)
        ]

        if (remainder := self.config.pages_count % self.config.batch_size) > 0:
            res.append(remainder)

        return tuple(res)

    async def _process_page(
        self,
        session: ClientSession,
        page_num: int
    ) -> None:
        page_url: str = self._ideas_link_generator(page_num)

        page: Html = await self._load_url(session, page_url)
        links: list[str] = get_card_links(page)

        tasks: list[Task] = [
            create_task(self._process_card(session, link))
            for link in links
        ]

        log.info(f"Loading page {page_num}")
        for idea in await gather(*tasks):
            if idea is not None:
                self.ideas.append(idea)
    
    async def _process_card(
        self,
        session: ClientSession,
        link: str
    ) -> Optional[Idea]:
        base_url: str = domain.format(lang=self.config.lang.value)
        card: Html =  await self._load_url(session, base_url + link)
        return parse_card(card)


    async def _load_url(self, session: ClientSession, url: str) -> Html:
        async with session.get(url) as r:
            return await r.text()


    def _ideas_link_generator(self, page_num: int) -> str:
        page: str = "" if page_num == 1 else f"page-{page_num}/"
        return base_ideas_url.format(
            lang=self.config.lang.value,
            asset=self.config.asset.lower(),
            page=page
        )

