import asyncio
from parser.TradingViewScraper import TradingViewScraper
from parser.types import Lang
from parser.models import ParserConfig 
from loguru import logger as log


def main() -> None:
    asyncio.run(driver())


async def driver() -> None:
    config: ParserConfig = ParserConfig(Lang.RU, 20, "BTCUSDT")
    parser: TradingViewScraper = TradingViewScraper(config)

    log.info(f"Parser created with config {config}")
    await parser.load_ideas()


if __name__ == "__main__":
    main()

