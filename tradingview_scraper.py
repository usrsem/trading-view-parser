import pandas as pd
from typing import Any
from requests_html import HTMLSession
from trading_types import ParserConfig, Lang, Asset
from config import base_page_url, base_ideas_url

import datetime


def page_link_generator(lang: Lang, page_num: int) -> str:
    page: str = "" if page_num == 1 else f"page-{page_num}/"
    return base_page_url.format(lang=lang.value, page=page)


def ideas_link_generator(lang: Lang, asset: Asset, page_num: int) -> str:
    page: str = "" if page_num == 1 else f"page-{page_num}/"
    return base_ideas_url.format(lang=lang.value, asset=asset, page=page)


class TradingParserException(Exception): pass


class TradingViewParser:

    def __init__(self, config: ParserConfig, chunk_size: int = 10):
        self.config: ParserConfig = config
        self.chunk_size = chunk_size
        self.session = HTMLSession()
        self.pages: dict[int, tuple[Any]] = {}
	
    # TODO: Create chunk_size async tasks for getting ideas pages
    # do while pages count < config.pages_count
    # Each chunk of loaded pages validate with validate_ticker
    # Store them in dict with structure {chunk_num: tuple of pages}

    # use aiohttp library and asyncio tasks
    # https://www.twilio.com/blog/asynchronous-http-requests-in-python-with-aiohttp
    # use ensure_task, not ensure_future

    # If send all reaquest withput waiting, trading view will ban u
    # After each chunk of requests create task for sleeping using asyncion.sleep
    def get_ideas(self):
        return self.session.get(ideas_link_generator(
            self.config.lang,
            self.config.asset,
            self.current_page
        ))

    # TODO: Move html parse logic to separate class
    def validate_ticker(self):
		erroreous_title = "Page not found — TradingView"
		r = self.get_ideas_for_ticker()
		r_title = r.html.find('#title', first=True).text
		if r_title == erroreous_title:
			raise Exception ("Page not found, check your input data")
		else: 
			return f"{self.asset} TW page is being parsed"
	
	def return_all_languages(self,page):

		if self.current_page < 2:
			languages = page.html.find('.tv-dropdown-behavior__body tv-header__dropdown-body js-lang-dropdown-list-desktop i-hidden')
			
			print('langs 1',[i.attrs['vertical-align: inherit'].text for i in languages])
		else:
			print('langs 2', languages)
			print('langs 3',[i for i in languages])
			print('langs 1',[i.attrs['vertical-align: inherit'].text for i in languages])
				
	def return_cards(self, page):
		# print('page',page.html.find('.tv-feed__item '))
		cards = [card for card in page.html.find('.tv-feed__item') if card.attrs['data-widget-type'] == 'idea']
		return cards
			

	def get_username(self, page):
		username = page.html.find('.tv-user-link__wrap', first=True).attrs['data-username']
	
		return username

	def get_exchange_with_ticker(self, page):
		
		data= page.html.find('.tv-chart-view__symbol--desc', first=True)
		if data != None:
			exchange, ticker = data.text.split(':')
			return exchange, ticker
		else:
			return None, None

	def get_link(self, card):
		link = list(card.find('.tv-widget-idea__title-row', first=True).absolute_links)[0]
	
		return link
	
	def get_date(self, page):
		date = page.html.find('.tv-chart-view__title-time', first=True).attrs['data-timestamp']
		dt = datetime.datetime.utcfromtimestamp(int(float(date)))
		return dt

	def get_idea_page(self, link):
	
		idea_page = HTMLSession().get(link)
		# idea_page.html.render()
		return idea_page
		
	def get_likes(self,page):
		likes = page.html.find('.tv-card-social-item__count', first=True).text
		return int(likes)
	
	def get_comments(self, page):
		try:
			cmmts = []
			comment_page = page.html.find('#chart-view-comments', first=True)
			comments = comment_page.find('.tv-chart-comment')
			cmt = []
			
			for comment in comments:
				if comment != None:
					username = comment.find('.js-userlink-popup', first=True).attrs['data-username']
					text = comment.find('.js-chart-comment__text', first=True).text
					time = comment.find('.tv-chart-comment__time', first=True).attrs['data-timestamp']
					
					dt = datetime.datetime.utcfromtimestamp(int(float(time)))
					if comment.attrs['data-depth'] == 0:
							cmt = []
							cmt.append([username,text,dt])
					elif comment.attrs['data-depth'] == 1:
							cmt[-1].append([username, text, dt])
					elif comment.attrs['data-depth'] == 2:
							cmt[-1][-1].append([username, text, dt])
				cmmts.append(cmt)
			else:
				return []
			return cmmts
		except Exception as e:
			print(e)
			return None
			
	
	def get_decription(self, 	page):
		description_text = page.html.find('.tv-chart-view__description-wrap ', first=True).text
		if description_text == None:
			return None
		return description_text
		
	def get_direction(self, page):

			direction_data = page.html.find('.tv-idea-label', first=True)
			if direction_data != None:
				if direction_data.attrs['class'][1] == 'tv-idea-label--long':
					return 'long'
				elif direction_data.attrs['class'][1] == 'tv-idea-label--short':
					return 'short'
			else:
				return None	
			
	def  idea_to_df(self,page):
				
				data = {'ticker':self.get_exchange_with_ticker(page)[1], 'exchange':self.get_exchange_with_ticker(page)[0], 'text':self.get_decription(page), 'direction':self.get_direction(page),  'date':self.get_date(page),'user':str(self.get_username(page)),'likes':self.get_likes(page),'comments':str(self.get_comments(page))}
				return data

	def ideas_df(self,cards):
		dfs = []
		for card in cards:
			
			link = self.get_link(card)
			page = self.get_idea_page(link)
			data = self.idea_to_df(page)
			
			dfs.append(pd.DataFrame([data]))
		dfss = pd.concat(dfs)
		dfss.index = pd.to_datetime(dfss.date)
		dfss.drop('date',axis=1)
		return dfss
		
if __name__ == "__main__":
    config: ParserConfig = ParserConfig(Lang.RU, 2, "BTCUSDT")
    parser: TradingViewParser = TradingViewParser(config)
    parser.get_ideas()

