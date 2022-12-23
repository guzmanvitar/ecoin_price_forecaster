"""Runs the crawling job. Run

    python src/crawler/crawl.py --help

for usage help.
"""

import argparse

from scrapy.crawler import CrawlerProcess

from src.crawler.settings import (
    CONCURRENT_REQUESTS,
    DOWNLOAD_DELAY,
    REQUEST_FINGERPRINTER_IMPLEMENTATION,
    ROBOTSTXT_OBEY,
    TWISTED_REACTOR,
)
from src.crawler.spiders.coingecko_spider import CoingeckoSpider
from src.logger_definition import get_logger
from src.utils import str2bool

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

    parser.add_argument(
        "-d",
        "--db_store",
        required=False,
        type=str2bool,
        default=False,
        nargs="?",
        const=True,
        help="Define wether to store in database or not",
    )

    args = parser.parse_args()

    # Select json pipeline or db and json pipeline based on comand line input
    if args.db_store:
        ITEM_PIPELINES = {
            "src.crawler.pipelines.CoingeckoCrawlerDbPipeline": 300,
        }
    else:
        ITEM_PIPELINES = {
            "src.crawler.pipelines.CoingeckoCrawlerJsonPipeline": 300,
        }

    # Create crawler process with configurations
    # TODO: add automatic import from settings using scrapy functions
    process = CrawlerProcess(
        settings={
            "CONCURRENT_REQUESTS": CONCURRENT_REQUESTS,
            "ITEM_PIPELINES": ITEM_PIPELINES,
            "ROBOTSTXT_OBEY": ROBOTSTXT_OBEY,
            "REQUEST_FINGERPRINTER_IMPLEMENTATION": REQUEST_FINGERPRINTER_IMPLEMENTATION,
            "TWISTED_REACTOR": TWISTED_REACTOR,
            "DOWNLOAD_DELAY": DOWNLOAD_DELAY,
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
