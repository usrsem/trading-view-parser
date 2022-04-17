from parser.types import Asset


assets: tuple[Asset] = tuple(["ETCUSDT"]) 

domain: str = "https://{lang}.tradingview.com"
base_page_url: str = "https://{lang}.tradingview.com/markets/cryptocurrencies/ideas/{page}?sort=recent"
base_ideas_url: str = "https://{lang}.tradingview.com/ideas/{asset}/{page}?sort=recent"

