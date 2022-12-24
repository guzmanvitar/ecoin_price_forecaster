import json
from pathlib import Path

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

POSTGRESDB_CON_STRING = "postgresql://admin:admin@database:5432/postgresdb"

API_DATE_FORMAT = "%d-%m-%Y"

# TODO: Improve this
with open(SECRETS / "twitter_credentials.json") as f:
    TWITTER_CREDENTIALS = json.load(f)
