"""Defines the sql alchemy tables to be created

See documentation in: https://docs.sqlalchemy.org/en/20/orm/extensions/declarative/api.html
"""

from sqlalchemy import Column, Date, Float, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


# Define table class
class Coingecko(Base):
    __tablename__ = "coingecko"

    coin_id = Column(String(15), primary_key=True)
    date = Column(Date, primary_key=True)
    currency = Column(String(3))
    current_price = Column(Float)
    market_cap = Column(Float)
    total_volume = Column(Float)
