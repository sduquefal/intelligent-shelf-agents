import os
from pathlib import Path

from dotenv import load_dotenv


ROOT_DIR = Path(__file__).resolve().parent.parent

load_dotenv(ROOT_DIR / ".env")


GCP_PROJECT = os.environ["GOOGLE_CLOUD_PROJECT"]
GCP_LOCATION = os.getenv(
    "GOOGLE_CLOUD_LOCATION",
    "us-east1",
)

BQ_PROJECT = os.environ["IS_BQ_PROJECT"]
BQ_DATASET = os.environ["IS_BQ_DATASET"]
NSG_REPORT_VIEW = os.environ["IS_NSG_REPORT_VIEW"]

NSG_REPORT_TABLE = (
    f"{BQ_PROJECT}.{BQ_DATASET}.{NSG_REPORT_VIEW}"
)