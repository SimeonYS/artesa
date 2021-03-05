import re

import scrapy

from scrapy.loader import ItemLoader
from ..items import ArtesaItem
from itemloaders.processors import TakeFirst
pattern = r'(\xa0)?'

class ArtesaSpider(scrapy.Spider):
	name = 'artesa'
	start_urls = ['https://www.artesa.cz/o-nas/aktuality/aktuality/']

	def parse(self, response):
		post_links = response.xpath('//h3/a/@href').getall()
		yield from response.follow_all(post_links, self.parse_post)

		next_page = response.xpath('//li[@class="last next"]/a/@href').get()
		if next_page:
			yield response.follow(next_page, self.parse)


	def parse_post(self, response):

		date = response.xpath('//time/@datetime').get()
		title = response.xpath('//div[@class="header"]/h1/text()').get()
		content = response.xpath('//div[@class="teaser-text"]//text()').getall() + response.xpath('//div[@class="news-text-wrap"]//text()').getall()
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "",' '.join(content))

		item = ItemLoader(item=ArtesaItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		yield item.load_item()
