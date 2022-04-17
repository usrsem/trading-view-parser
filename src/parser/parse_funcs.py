from datetime import datetime
from typing import Optional
from bs4 import BeautifulSoup
from datetime import datetime
from parser.models import Idea
from parser.types import Direction, Html
from loguru import logger as log


class ParsingException(Exception): pass


def parse_cards(cards: tuple[Html, ...]) -> list[Idea]:
    ideas = []
    for card in cards:
        if (idea := parse_card(card)) is not None:
            ideas.append(idea)

    return ideas


def parse_card(card: Html) -> Optional[Idea]:
    soup: BeautifulSoup = BeautifulSoup(card, "html.parser")

    try:
        exchange, ticker = _get_exchange_with_ticker(soup)
        res = Idea(
            username=_get_username(soup),
            likes_count=_get_likes_count(soup),
            date=_get_date(soup),
            directon=_get_direction(soup),
            exchange=exchange,
            ticker=ticker,
            description=_get_description(soup)
        )
    except ParsingException as e:
        log.warning(e)
        return None

    return res


def get_card_links(page: Html) -> list[str]:
    soup: BeautifulSoup = BeautifulSoup(page, "html.parser")
    return [
        _get_link(card)
        for card in _get_cards(soup)
    ]


def _get_cards(soup: BeautifulSoup) -> list[BeautifulSoup]:
    return [
        card
        for card in soup.find_all("div", {"class": "tv-feed__item"})
        if card.attrs["data-widget-type"] == "idea"
    ]


def _get_link(soup: BeautifulSoup) -> str:
    link = soup.find("a", {"class": "tv-widget-idea__title"})
    if link is not None:
        return link.get("href")

    raise ParsingException("Can't find link of card")


def _get_username(soup: BeautifulSoup) -> str:
    username = soup.find("a", {"class": "tv-user-link__wrap"})

    if username is not None:
        return username.get("data-username")

    raise ParsingException("Can't find username in card") 


def _get_exchange_with_ticker(soup: BeautifulSoup) -> tuple[str, str]:
    data = soup.find("a", {"class": "tv-chart-view__symbol--desc"})
    if data is not None:
        return tuple(data.text.split(":"))

    raise ParsingException("Can't find exchange with ticker in card")


def _get_date(soup: BeautifulSoup) -> datetime:
    date = soup.find("span", {"class": "tv-chart-view__title-time"})

    if date is not None:
        try:
            return datetime.utcfromtimestamp(
                    int(float(date.get("data-timestamp"))))
        except ValueError:
            raise ParsingException(
                    f"Can't parse datetime {date.get('data-timestamp')}")


    raise ParsingException("Can't find date in card")


def _get_likes_count(soup: BeautifulSoup) -> int:
    likes = soup.find("span", {"class": "tv-card-social-item__count"})

    if likes is not None:
        try:
            return int(likes.text)
        except ValueError:
            raise ParsingException(f"Likes count is not a number {likes.text}")

    raise ParsingException("Can't find likes count in card")


def _get_direction(soup: BeautifulSoup) -> Direction:
    direction = soup.find("span", {"class": "badge-yHuWj4ze"})

    if direction is not None:
        return Direction.LONG if "long" in direction else Direction.SHORT

    return Direction.NOT_FOUND


def _get_description(soup: BeautifulSoup) -> str:
    description = soup.find("div", {"class": "tv-chart-view__description-wrap"})

    if description is not None:
        return description.text.replace("\n", " ")

    raise ParsingException("Can't find description in card")

