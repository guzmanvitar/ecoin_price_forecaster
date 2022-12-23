import json

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.constants import DATA_RAW
from src.db_scripts import db_mappings


class CoingeckoCrawlerDbPipeline:
    # Define conection string to acces postre database. Note that the string follows docker
    # formating rules and uses name, user and password as defined in docker compose db service.
    CON_STRING = "postgresql://admin:admin@database:5432/postgresdb"

    def __init__(self):
        self.create_engine()
        self.create_table()
        self.define_session()

    def create_engine(self):
        self.engine = create_engine(self.CON_STRING)

    def create_table(self):
        db_mappings.Base.metadata.create_all(self.engine)

    def define_session(self):
        self.Session = sessionmaker(bind=self.engine)

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
        with self.Session() as my_session:
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
