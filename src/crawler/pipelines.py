"""Implements logic for processing scrapped items.

Every item that we yield in our spiders will be processed through this script. We define to post
processing pipelines here, one dumps the scraped item to local folder, the other dumps the json
and also stores the item in a database.

More info: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
"""

import json

from src.constants import DATA_COINGECKO
from src.db_scripts import db_connection, db_mappings


class CoingeckoCrawlerDbPipeline:
    def __init__(self):
        self.db = db_connection.PostgresDb()

    def process_item(self, item, spider):
        self.storeitems(item)
        return item

    def storeitems(self, item):
        # # JSON DUMP
        # convert scrapy item to json
        item_dict = dict(item)

        # convert date to string
        item_dict["date"] = str(item_dict["date"])

        # Local json dump
        date = item_dict["date"]
        coin = item_dict["coin_id"]

        write_path = DATA_COINGECKO / f"{coin}_{date}.json"

        with open(str(write_path), "w") as f:
            json.dump(item_dict, f)

        # # DB STORAGE
        with self.db.Session() as my_session:
            # Db storage
            my_session.begin()
            # NOTE: Use of merge (instead of add) allows for update registry if crawled item is
            # repeated
            my_session.merge(db_mappings.CoingeckoScrapedData(**item_dict))
            my_session.commit()


class CoingeckoCrawlerJsonPipeline:
    def process_item(self, item, spider):
        self.storeitems(item)
        return item

    def storeitems(self, item):
        # TODO: Create parent class to avoid repeated code below
        # convert scrapy item to json
        item_dict = dict(item)

        # convert date to string
        item_dict["date"] = str(item_dict["date"])

        # Local json dump
        date = item_dict["date"]
        coin = item_dict["coin_id"]

        write_path = DATA_COINGECKO / f"{coin}_{date}.json"

        with open(str(write_path), "w") as f:
            json.dump(item_dict, f)
