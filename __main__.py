import asyncio
from tradingview_scraper import TradingViewParser
from trading_types import ParserConfig, Lang
from loguru import logger as log


async def main() -> None:
    config: ParserConfig = ParserConfig(Lang.RU, 20, "BTCUSDT")
    parser: TradingViewParser = TradingViewParser(config)
    log.info("Parser created")
    await parser.get_ideas()


if __name__ == "__main__":
    asyncio.run(main())

