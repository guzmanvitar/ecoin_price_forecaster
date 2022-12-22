from pathlib import Path

this = Path(__file__)

ROOT = this.parents[1]

LOGS = ROOT / "logs"

DATA = ROOT / "data"

DATA_RAW = DATA / "raw"
DATA_READY = DATA / "ready"
DATA_INTERIM = DATA / "interim"

DATA_RAW.mkdir(exist_ok=True, parents=True)
DATA_READY.mkdir(exist_ok=True, parents=True)
DATA_INTERIM.mkdir(exist_ok=True, parents=True)

DATE_FORMAT = "%d-%m-%Y"
