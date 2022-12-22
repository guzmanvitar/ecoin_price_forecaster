import json
from datetime import datetime, timedelta

import scrapy

from src.constants import DATE_FORMAT
from src.crawler.items import CoingeckoItem


class CoingeckoSpider(scrapy.Spider):
    # Scraper attributes
    name = "coingecko_spider"

    def __init__(self, coin_ids: list[str], start_date: str, end_date: str | None = None):
        if not coin_ids:
            raise ValueError("Coin ids parameter can't be null")
        elif not isinstance("bitcoin", list):
            self.coin_ids = [coin_ids]
        else:
            self.coin_ids = coin_ids

        if not start_date:
            raise ValueError("Start date parameter can't be null")
        else:
            self.start_date = datetime.strptime(start_date, DATE_FORMAT).date()

        if not end_date:
            self.end_date = datetime.strptime(start_date, DATE_FORMAT).date()
        else:
            self.end_date = datetime.strptime(end_date, DATE_FORMAT).date()

    def start_requests(self):
        delta_dates = (self.end_date - self.start_date).days

        date_range = [self.start_date + timedelta(days=i) for i in range(delta_dates + 1)]
        date_range_str = [date.strftime(DATE_FORMAT) for date in date_range]

        crawl_list = [
            (
                f"https://api.coingecko.com/api/v3/coins/{coin_id}/history?date={str_date}",
                coin_id,
                str_date,
            )
            for coin_id in self.coin_ids
            for str_date in date_range_str
        ]

        for url, coin_id, date in crawl_list:
            yield scrapy.Request(
                url=url,
                callback=self.parse,
                headers={
                    "Accept": "application/json",
                    "User-Agent": (
                        "Mozilla/5.0 (X11; Linux x86_64; rv:48.0) Gecko/20100101 Firefox/48.0"
                    ),
                },
                meta={"coin_id": coin_id, "date": date},
            )

    def parse(self, response):
        # Load API response
        json_response = json.loads(response.text)

        # Scrape relevant data
        current_price = json_response["market_data"]["current_price"]["usd"]
        market_cap = json_response["market_data"]["market_cap"]["usd"]
        total_volume = json_response["market_data"]["total_volume"]["usd"]

        # Define and populate Item
        item = CoingeckoItem()

        item["coin_id"] = response.meta["coin_id"]
        item["scraped_date"] = response.meta["date"]
        item["currency"] = "usd"
        item["current_price"] = current_price
        item["market_cap"] = market_cap
        item["total_volume"] = total_volume

        # Yield item to be stored in database
        yield item
