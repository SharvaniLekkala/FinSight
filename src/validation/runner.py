import logging
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine

from src.validation.rules import (
    check_missing_values,
    check_duplicates,
    check_invalid_transactions,
    check_null_identifiers,
)

logger = logging.getLogger(__name__)

def run_validation(table_name: str, engine, config):
    """Load a staging table into a DataFrame and run all validation rules.
    Results are written to a validation_log table.
    """
    logger.info("Running validation on %s", table_name)
    df = pd.read_sql_table(table_name, con=engine)
    results = []
    # Determine required columns based on dataset type
    if table_name == "stg_paysim_raw":
        required = ["step", "type", "amount", "nameOrig", "oldbalanceOrg", "newbalanceOrig", "nameDest", "oldbalanceDest", "newbalanceDest", "isFraud", "isFlaggedFraud"]
        id_cols = ["nameOrig", "nameDest"]
    else:  # credit raw
        required = ["ID", "LIMIT_BAL", "SEX", "EDUCATION", "MARRIAGE", "AGE", "PAY_0", "PAY_2", "PAY_3", "PAY_4", "PAY_5", "PAY_6", "BILL_AMT1", "PAY_AMT1", "default.payment.next.month"]
        id_cols = ["ID"]
    results.append(check_missing_values(df, required))
    results.append(check_duplicates(df, required))
    results.append(check_invalid_transactions(df))
    results.append(check_null_identifiers(df, id_cols))

    # Write results to validation_log table (create if not exists)
    create_sql = """
    CREATE TABLE IF NOT EXISTS validation_log (
        id SERIAL PRIMARY KEY,
        table_name TEXT,
        rule_name TEXT,
        passed BOOLEAN,
        issue_count INT,
        run_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    engine.execute(create_sql)
    insert_sql = """
    INSERT INTO validation_log (table_name, rule_name, passed, issue_count)
    VALUES (%s, %s, %s, %s);
    """
    for r in results:
        engine.execute(insert_sql, (table_name, r.rule_name, r.passed, r.issue_count))
        logger.info("Rule %s passed=%s issues=%d", r.rule_name, r.passed, r.issue_count)

if __name__ == "__main__":
    # Simple CLI for manual runs
    import argparse
    parser = argparse.ArgumentParser(description="Run validation on staging tables")
    parser.add_argument("--config", default="config/db.yaml")
    args = parser.parse_args()
    engine = create_engine(
        f"postgresql+psycopg2://{args.config}"  # placeholder, adjust in real use
    )
    # For demo purpose, run on both tables
    for tbl in ["stg_paysim_raw", "stg_credit_raw"]:
        run_validation(tbl, engine, None)
