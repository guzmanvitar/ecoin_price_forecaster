"""Impelements coingecko_spider soider class for coingecko crawling.

For a better understanding to this code check basic scrapy logic at
https://docs.scrapy.org/en/latest/intro/tutorial.html
"""

import json
from collections.abc import Iterator
from datetime import date, timedelta

import scrapy

from src.constants import API_DATE_FORMAT
from src.crawler.items import CoingeckoItem


class CoingeckoSpider(scrapy.Spider):
    """Spider class supporting main coingecko scraping logic.

    Args:
        coin_id (str): coin id to scrape, ex. bitcoin
        start_date (str): start of date range to scrape in iso format
        end_date (str): end of date range to scrape in iso format

    Raises:
        ValueError: coin_id parameter cant be null
        ValueError: start_date parameter cant be null

    Yields:
        CoingeckoItem: scrapy item for further processing, in particular scrapy will use this
            yielded item to populate the database.
    """

    # Spider attributes
    name = "coingecko_spider"

    def __init__(self, coin_id: str, start_date: str, end_date: str | None = None):
        if not coin_id:
            raise ValueError("Coin ids parameter can't be null")
        else:
            self.coin_ids = [coin_id]  # TODO: add list of strings possibility

        if not start_date:
            raise ValueError("Start date parameter can't be null")
        else:
            self.start_date = date.fromisoformat(start_date)

        if not end_date:
            self.end_date = date.fromisoformat(start_date)
        else:
            self.end_date = date.fromisoformat(end_date)

        self.logger.logger.name = f"crawler.{CoingeckoSpider.name}"

    def start_requests(self) -> Iterator[scrapy.Request]:
        """Makes initial scrapy requests to coingecko API.

        This method is usually combined in scrapy with further requests for pagination or for
        further exploration of new urls found in initial scraping. In this case though, the initial
        requests are all the requests we'll do.

        Yields:
            Iterator[scrapy.Request]: The initial request.
        """
        # Build date list to crawl
        delta_dates = (self.end_date - self.start_date).days
        date_range = [self.start_date + timedelta(days=i) for i in range(delta_dates + 1)]

        # Build url list to crawl
        crawl_list = [
            (
                (
                    f"https://api.coingecko.com/api/v3/coins/{coin_id}/"
                    f"history?date={target_date.strftime(API_DATE_FORMAT) }"
                ),
                coin_id,
                target_date,
            )
            for coin_id in self.coin_ids  # currently len(coin_ids) is always 1
            for target_date in date_range
        ]

        self.logger.info(f"Preparing to scrape {len(crawl_list)} urls.")

        for url, coin_id, target_date in crawl_list:
            yield scrapy.Request(
                url=url,
                callback=self.parse,  # yielded requests are processed through the parse callback
                headers={
                    "Accept": "application/json",
                    "User-Agent": (
                        "Mozilla/5.0 (X11; Linux x86_64; rv:48.0) Gecko/20100101 Firefox/48.0"
                    ),
                },
                meta={"coin_id": coin_id, "target_date": target_date},
            )

    def parse(self, response) -> Iterator[CoingeckoItem]:
        """Processor for API request response.

        Recieves text response from API, extracts relevant information, loads said information to a
        scrapy item and yields said item for further processing in the pipelines.py script.

        Args:
            response (http.TextResponse): The responses for the crawl list defined in the
                start_requests method.

        Yields:
            Iterator[CoingeckoItem]: A scrapy item, defined for this particular scraper.
        """
        # Load API response
        json_response = json.loads(response.text)

        # Scrape relevant data
        usd_price = json_response["market_data"]["current_price"]["usd"]

        # Define and populate Item
        item = CoingeckoItem()

        item["coin_id"] = response.meta["coin_id"]
        item["date"] = response.meta["target_date"]
        item["usd_price"] = usd_price
        item["full_response"] = json_response

        # Yield item to be stored in database
        yield item
