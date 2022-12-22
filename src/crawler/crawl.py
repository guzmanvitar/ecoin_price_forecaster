"""Runs the crawling job. Run

    python src/crawler/crawl.py --help

for usage help.
"""

import argparse

from scrapy.crawler import CrawlerProcess
from scrapy.spiderloader import SpiderLoader
from scrapy.utils.project import get_project_settings

# https://docs.scrapy.org/en/latest/topics/practices.html#run-scrapy-from-a-script
# https://docs.scrapy.org/en/latest/topics/api.html#scrapy.crawler.CrawlerProcess

if __name__ == "__main__":
    settings = get_project_settings()

    spiders = SpiderLoader(settings).list()

    parser = argparse.ArgumentParser("crawler")

    parser.add_argument(
        "--spiders",
        nargs="*",
        default=spiders,
        choices=spiders,
        help="Spiders to crawl. By default, use all spiders discoverable by scrapy's SpiderLoader.",
    )

    parser.add_argument(
        "-c",
        "--coin_ids",
        nargs="+",
        required=True,
        type=str,
        choices=["bitcoin", "ethereum", "cardano"],
        help="List of coin ids to scrape",
    )

    parser.add_argument(
        "-s",
        "--start_date",
        required=True,
        type=str,
        help="Start of range of dates to scrape in dd-mm-yyyy format",
    )

    parser.add_argument(
        "-e",
        "--end_date",
        required=False,
        type=str,
        help="End of range of dates to scrape in dd-mm-yyyy format",
    )

    args = parser.parse_args()

    process = CrawlerProcess(settings, install_root_handler=False)
    for spider in args.spiders:
        process.crawl(
            spider, coin_ids=args.coin_ids, start_date=args.start_date, end_date=args.end_date
        )
    process.start()
