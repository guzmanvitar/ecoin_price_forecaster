"""Defines project wide constants

"""
from pathlib import Path

# Path constants
this = Path(__file__)

ROOT = this.parents[1]

LOGS = ROOT / "logs"

DATA = ROOT / "data"

SECRETS = ROOT / ".secrets"

DATA_RAW = DATA / "raw"
DATA_READY = DATA / "ready"
DATA_INTERIM = DATA / "interim"
DATA_TWITTER = DATA_RAW / "twitter"

DATA_READY.mkdir(exist_ok=True, parents=True)
DATA_INTERIM.mkdir(exist_ok=True, parents=True)
DATA_TWITTER.mkdir(exist_ok=True, parents=True)

# Postgres connection, as defined by sqlalchemy formating, and by user, password and name defined in
# docker compose service.
POSTGRESDB_CON_STRING = "postgresql://admin:admin@database:5432/postgresdb"

# Coingecko API date format
API_DATE_FORMAT = "%d-%m-%Y"
