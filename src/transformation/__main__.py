import argparse
import logging
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine

from src.transformation.clean_paysim import clean_paysim
from src.transformation.clean_credit import clean_credit
from src.ingestion.loader import load_db_engine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description="FinSight transformation pipeline")
    parser.add_argument("--config", default="config/db.yaml", help="Path to DB config yaml")
    args = parser.parse_args()

    engine = load_db_engine(args.config)

    # Process PaySim
    paysim_df = pd.read_sql_table("stg_paysim_raw", con=engine)
    paysim_clean = clean_paysim(paysim_df)
    with engine.begin() as conn:
        conn.exec_driver_sql("DROP TABLE IF EXISTS transformed_paysim CASCADE;")
    paysim_clean.to_sql("transformed_paysim", con=engine, if_exists="replace", index=False, method="multi", chunksize=500)
    logger.info("Transformed PaySim: %d rows", len(paysim_clean))

    # Process Credit
    credit_df = pd.read_sql_table("stg_credit_raw", con=engine)
    credit_clean = clean_credit(credit_df)
    with engine.begin() as conn:
        conn.exec_driver_sql("DROP TABLE IF EXISTS transformed_credit CASCADE;")
    credit_clean.to_sql("transformed_credit", con=engine, if_exists="replace", index=False, method="multi", chunksize=500)
    logger.info("Transformed Credit: %d rows", len(credit_clean))

if __name__ == "__main__":
    main()
