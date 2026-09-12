import argparse
import logging
from pathlib import Path

from src.ingestion.loader import ingest_dataset, load_db_engine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description="FinSight data ingestion pipeline")
    parser.add_argument("--config", default="config/db.yaml", help="Path to DB config yaml")
    args = parser.parse_args()

    engine = load_db_engine(args.config)

    # Dataset definitions: name, URL, staging table name
    datasets = [
        {
            "name": "paysim",
            "url": "https://raw.githubusercontent.com/ntumg/paysim/master/data/paysim.csv",
            "staging_table": "stg_paysim_raw",
        },
        {
            "name": "credit",
            "url": "https://archive.ics.uci.edu/ml/machine-learning-databases/00350/default%20of%20credit%20card%20clients.xls",
            "staging_table": "stg_credit_raw",
        },
    ]

    for ds in datasets:
        logger.info("Starting ingestion for %s", ds["name"])
        ingest_dataset(
            name=ds["name"],
            url=ds["url"],
            staging_table=ds["staging_table"],
            engine=engine,
        )

if __name__ == "__main__":
    main()
