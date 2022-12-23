import json

from src.constants import DATA_RAW
from src.db_scripts import db_connection, db_mappings


class CoingeckoCrawlerDbPipeline:
    def __init__(self):
        self.db = db_connection.PostgreDb()

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

        write_path = DATA_RAW / f"{coin}_{date}.json"

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
        # convert scrapy item to json
        item_dict = dict(item)

        # convert date to string
        item_dict["date"] = str(item_dict["date"])

        # Local json dump
        date = item_dict["date"]
        coin = item_dict["coin_id"]

        write_path = DATA_RAW / f"{coin}_{date}.json"

        with open(str(write_path), "w") as f:
            json.dump(item_dict, f)
