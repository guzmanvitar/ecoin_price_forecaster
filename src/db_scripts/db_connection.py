"""Defines docker postgres database conection and querying utilities.

"""

import pandas as pd
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.constants import POSTGRESDB_CON_STRING
from src.db_scripts import db_mappings


class PostgreDb:
    """Class containing database conection and querying functionality.

    Note that the query string imported from constants follows docker formating rules and uses
    name, user and password as defined in docker compose db service.
    """

    def __init__(self, constring: str = POSTGRESDB_CON_STRING):
        self._constring = constring
        self._create_engine(constring)
        self._create_table()
        self._define_session()

    def _create_engine(self, constring: str):
        """Initializes sqlalchemy connection based on a sqlalchemy connection string.

        More info at: https://docs.sqlalchemy.org/en/20/core/engines.html

        Args:
            constring (str): sqlalchemy connection string.
        """
        self.engine = create_engine(constring)

    def _create_table(self):
        """Initializes all tables defined in db_mappings on the database conected to self.engine."""
        db_mappings.Base.metadata.create_all(self.engine)

    def _define_session(self):
        """Starts a sqlalchemy session needed for table operations.

        More on sqlalchemy sessions: https://docs.sqlalchemy.org/en/14/orm/session.html
        """
        self.Session = sessionmaker(bind=self.engine)

    def execute_query(self, query_str: str) -> pd.DataFrame:
        """Queries the database and returns a pandas dataframe

        Args:
            query_str (str): sql query in string format

        Returns:
            pd.DataFrame: output dataframe
        """
        return pd.read_sql(query_str, con=self.engine)

    def update_table_from_pandas(
        self, df: pd.DataFrame, declarative_base: sqlalchemy.orm.decl_api.DeclarativeMeta
    ):
        """Updates a given table with rows from a pandas dataframe

        Args:
            df (pd.DataFrame): dataframe to load
            declarative_base (sqlalchemy.orm.decl_api.DeclarativeMeta): table to impact
        """
        for row_dict in df.to_dict(orient="records"):
            with self.Session() as my_session:
                my_session.begin()
                my_session.merge(declarative_base(**row_dict))
                my_session.commit()

    def create_maxmin_table(self) -> pd.DataFrame:
        """Queries the raw scrape database and creates the table 2 (min max) of the exam, returning
        it as a pandas dataframe

        Returns:
            pd.DataFrame: pandas dataframe with processed table
        """
        maxmin_query = """
            WITH monthly_data AS (
                SELECT
                    coin_id,
                    CONCAT(CAST(DATE_PART('year', date) AS VARCHAR(4)), '-',
                        CAST(DATE_PART('month', date) AS VARCHAR(2))) year_month,
                    usd_price
                FROM
                    coingecko_scraped_data)
            SELECT
                coin_id,
                year_month,
                MAX(usd_price) usd_price_max,
                MIN(usd_price) usd_price_min
            FROM
                monthly_data
            GROUP BY
                coin_id,
                year_month;
            """
        minmax_df = self.execute_query(maxmin_query)

        return minmax_df
