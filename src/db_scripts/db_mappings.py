"""Defines the sql alchemy tables to be created

See documentation in: https://docs.sqlalchemy.org/en/20/orm/extensions/declarative/api.html
"""

from sqlalchemy import Column, Date, Float, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


# Define table class
class CoingeckoScrapedData(Base):
    """Sqlalchemy table definition for the storage of scraped data."""

    __tablename__ = "coingecko_scraped_data"

    coin_id = Column(String(15), primary_key=True)
    date = Column(Date, primary_key=True)
    usd_price = Column(Float)
    full_response = Column(JSONB)
