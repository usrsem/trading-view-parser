from aiohttp import ClientSession
from asyncio import create_task, gather, sleep
from config import base_page_url, base_ideas_url
from loguru import logger as log
from typing import Any
from trading_types import ParserConfig, Lang


def page_link_generator(lang: Lang, page_num: int) -> str:
    page: str = "" if page_num == 1 else f"page-{page_num}/"
    return base_page_url.format(lang=lang.value, page=page)


class TradingParserException(Exception): pass


class TradingViewParser:

    def __init__(self, config: ParserConfig, chunk_size: int = 10):
        self.config: ParserConfig = config
        self.chunk_size = chunk_size
        self.pages: dict[int, tuple[Any]] = {}
	

    async def load_ideas(self):
        log.info("Startign parsing")

        async with ClientSession() as session:
            for chunk_num in range(self.config.pages_count // self.chunk_size):

                tasks = []
                for i in range(self.chunk_size):
                    tasks.append(create_task(self.get_page(session, i)))

                pages = await gather(*tasks)
                self.pages[chunk_num] = pages
                log.info(f"Loaded {len(pages)} pages")

                await sleep(1)

        log.info("Ending parsing")

    async def get_page(self, session: ClientSession, page_num: int) -> Any:
        async with session.get(self.ideas_link_generator(page_num)) as r:
            return await r.text()

    def ideas_link_generator(self, page_num: int) -> str:
        page: str = "" if page_num == 1 else f"page-{page_num}/"
        return base_ideas_url.format(
            lang=self.config.lang.value, asset=self.config.asset, page=page)

