import parser.config
from parser.TradingViewScraper import TradingViewScraper
from parser.types import Lang
from parser.models import ParserConfig


def _create_tv_parser() -> TradingViewScraper:
    config: ParserConfig = ParserConfig(
        Lang.EN,
        20,
        parser.config.assets[0]
    )

    return TradingViewScraper(config)


def test_page_num_generator() -> None:
    tv_parser = _create_tv_parser()
    undertest = tv_parser.page_num_generator()
    after = [i for i in undertest]
    mustbe = [i+1 for i in range(tv_parser.config.pages_count)]
    assert after == mustbe, f"{after=}, {mustbe=}"


def test_batches_iterator() -> None:
    # Pages count % batch size == 0
    tv_parser = _create_tv_parser()
    after = tv_parser.batches_iterator()
    mustbe = tuple([10, 10])
    assert after == mustbe, f"{after=}, {mustbe=}"

    # Pages count % batch size > 0
    tv_parser = _create_tv_parser()
    tv_parser.config = tv_parser.config._replace(pages_count=25)
    after = tv_parser.batches_iterator()
    mustbe = tuple([10, 10, 5])
    assert after == mustbe, f"{after=}, {mustbe=}"

    # Pages count < batch size
    tv_parser = _create_tv_parser()
    tv_parser.config = tv_parser.config._replace(batch_size=tv_parser.config.pages_count + 10)
    after = tv_parser.batches_iterator()
    mustbe = tuple([tv_parser.config.pages_count])
    assert after == mustbe, f"{after=}, {mustbe=}"

