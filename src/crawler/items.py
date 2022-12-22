# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class CoingeckoItem(scrapy.Item):
    # define the fields for your item here like:
    coin_id = scrapy.Field()
    date = scrapy.Field()
    currency = scrapy.Field()
    current_price = scrapy.Field()
    market_cap = scrapy.Field()
    total_volume = scrapy.Field()
