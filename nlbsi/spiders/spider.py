import datetime
import re

import scrapy

from scrapy.loader import ItemLoader

from ..items import NlbsiItem
from itemloaders.processors import TakeFirst


class NlbsiSpider(scrapy.Spider):
	name = 'nlbsi'
	start_urls = ['https://www.nlb.si/sporocila-za-javnost']

	def parse(self, response):
		now = datetime.datetime.now().year
		for year in range(1996, now + 1):
			year_url = f'https://www.nlb.si/sporocila-za-javnost?year={year}'
			yield response.follow(year_url, self.parse_year)

	def parse_year(self, response):
		post_links = response.xpath('//div[@class="col-sm-10 link"]/a/@href').getall()
		yield from response.follow_all(post_links, self.parse_post)

	def parse_post(self, response):
		if response.url[-10:] == 'izjava-kfi':
			return
		title = response.xpath('//h1//text()[normalize-space()]').get()
		description = response.xpath('//div[@class="contents"]//text()[normalize-space()and not(ancestor::a | ancestor::h1)]').getall()
		description = [p.strip() for p in description]
		description = ' '.join(description).strip()
		try:
			date = re.findall(r'\d+\.?\s*\w+\s\d{4}', description)[0]
		except:
			print(response.url)
			date = ''

		description = re.sub(r'\d+\.?\s*\w+\s\d{4}', '', description)

		item = ItemLoader(item=NlbsiItem(), response=response)
		item.default_output_processor = TakeFirst()
		item.add_value('title', title)
		item.add_value('description', description)
		item.add_value('date', date)

		return item.load_item()
