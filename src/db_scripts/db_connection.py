"""Defines database conection and querying utilities.

"""

import pandas as pd
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.constants import POSTGRESDB_CON_STRING
from src.db_scripts import db_mappings


class PostgreDb:
    """Class containing database conection and querying functionality."""

    def __init__(self, constring: str = POSTGRESDB_CON_STRING):
        self._constring = constring
        self._create_engine()
        self._create_table()
        self._define_session()

    def _create_engine(self):
        self.engine = create_engine(self._constring)

    def _create_table(self):
        db_mappings.Base.metadata.create_all(self.engine)

    def _define_session(self):
        self.Session = sessionmaker(bind=self.engine)

    def execute_query(self, query_str: str) -> pd.DataFrame:
        return pd.read_sql(query_str, con=self.engine)

    def update_table_from_pandas(
        self, df: pd.DataFrame, declarative_base: sqlalchemy.orm.decl_api.DeclarativeMeta
    ):
        for row_dict in df.to_dict(orient="records"):
            with self.Session() as my_session:
                my_session.begin()
                my_session.merge(declarative_base(**row_dict))
                my_session.commit()
