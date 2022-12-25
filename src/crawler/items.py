"""Defines the model for scraped items

See documentation in: https://docs.scrapy.org/en/latest/topics/items.html
"""

import scrapy


class CoingeckoItem(scrapy.Item):
    """A scrapy item abstraction needed for processing scraped items.

    Note thart this item will be loaded to the coingecko_scraped_data table, and thus, its fields
    must coincide with those defines in src.db_scripts.db_mappings.CoingeckoScrapedData

    Args:
        scrapy (_type_): _description_
    """

    # define the fields for your item here like:
    coin_id = scrapy.Field()
    date = scrapy.Field()
    usd_price = scrapy.Field()
    full_response = scrapy.Field()
