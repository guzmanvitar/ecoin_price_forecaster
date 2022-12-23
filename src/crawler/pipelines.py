from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.db_scripts import db_mappings


class CoingeckoCrawlerPipeline:
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
        self.putitemsintable(item)
        return item

    def putitemsintable(self, item):
        with self.Session() as my_session:
            my_session.begin()
            # NOTE: Use of merge (instead of add)allows to update registry if crawled item is
            # repeated
            my_session.merge(db_mappings.Coingecko(**dict(item)))
            my_session.commit()
