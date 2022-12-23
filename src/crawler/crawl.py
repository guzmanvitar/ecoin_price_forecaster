"""Runs the crawling job. Run

    python src/crawler/crawl.py --help

for usage help.
"""

import argparse

from scrapy.crawler import CrawlerProcess

from src.crawler.settings import CONCURRENT_REQUESTS, ITEM_PIPELINES, ROBOTSTXT_OBEY
from src.crawler.spiders.coingecko_spider import CoingeckoSpider
from src.logger_definition import get_logger

logger = get_logger(__file__)


# https://docs.scrapy.org/en/latest/topics/practices.html#run-scrapy-from-a-script
# https://docs.scrapy.org/en/latest/topics/api.html#scrapy.crawler.CrawlerProcess

if __name__ == "__main__":
    parser = argparse.ArgumentParser("crawler")

    parser.add_argument(
        # TODO: incorporate list of strings as argument to crawl various coins in one run
        "-c",
        "--coin_id",
        required=True,
        choices=["bitcoin", "ethereum", "cardano"],
        help="Coin id to scrape",
    )

    parser.add_argument(
        "-s",
        "--start_date",
        required=True,
        type=str,
        help="Start of range of dates to scrape in iso format",
    )

    parser.add_argument(
        "-e",
        "--end_date",
        required=False,
        type=str,
        help="End of range of dates to scrape in iso format",
    )

    args = parser.parse_args()

    process = CrawlerProcess(
        # TODO: fix automatic import from settings using scrapy functions
        settings={
            "CONCURRENT_REQUESTS": CONCURRENT_REQUESTS,
            "ITEM_PIPELINES": ITEM_PIPELINES,
            "ROBOTSTXT_OBEY": ROBOTSTXT_OBEY,
        }
    )
    process.crawl(
        CoingeckoSpider,
        coin_id=args.coin_id,
        start_date=args.start_date,
        end_date=args.end_date,
    )
    logger.info(f"Launching crawl for {CoingeckoSpider.name} spiders")
    process.start()
