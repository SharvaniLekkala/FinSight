import logging
from sqlalchemy import text
import pandas as pd
from src.ingestion.loader import load_db_engine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def populate_dim_customer(engine):
    logger.info("Populating dim_customer from transformed tables")
    # Union distinct customers from both datasets
    sql = text("""
    INSERT INTO dim_customer (customer_id, gender, education, marriage, age, age_group)
    SELECT DISTINCT customer_id,
        gender,
        education,
        marriage,
        age,
        age_group
    FROM (
        SELECT customer_id, NULL::TEXT AS gender, NULL::TEXT AS education, NULL::TEXT AS marriage,
               NULL::INT AS age, NULL::TEXT AS age_group FROM transformed_paysim
        UNION ALL
        SELECT customer_id::TEXT, sex AS gender, education::TEXT, marriage::TEXT, age::INT, age_group::TEXT FROM transformed_credit
    ) AS u
    ON CONFLICT (customer_id) DO NOTHING;
    """)
    with engine.begin() as conn:
        conn.execute(sql)

def populate_dim_account(engine):
    logger.info("Populating dim_account from PaySim data")
    sql = text("""
    INSERT INTO dim_account (account_id)
    SELECT DISTINCT merchant_id FROM transformed_paysim
    ON CONFLICT (account_id) DO NOTHING;
    """)
    with engine.begin() as conn:
        conn.execute(sql)

def populate_dim_date(engine):
    logger.info("Populating dim_date from transformed PaySim data (transaction timestamps)")
    sql = text("""
    INSERT INTO dim_date (date_key, date, year, month, day, weekday)
    SELECT DISTINCT date_key,
        DATE_TRUNC('day', transaction_timestamp)::DATE AS date,
        EXTRACT(YEAR FROM transaction_timestamp)::INT AS year,
        EXTRACT(MONTH FROM transaction_timestamp)::INT AS month,
        EXTRACT(DAY FROM transaction_timestamp)::INT AS day,
        EXTRACT(DOW FROM transaction_timestamp)::INT AS weekday
    FROM transformed_paysim
    ON CONFLICT (date_key) DO NOTHING;
    """)
    with engine.begin() as conn:
        conn.execute(sql)

def populate_dim_transaction_type(engine):
    logger.info("Populating dim_transaction_type from PaySim type codes")
    sql = text("""
    INSERT INTO dim_transaction_type (transaction_type, description)
    SELECT DISTINCT type, NULL FROM transformed_paysim
    ON CONFLICT (transaction_type) DO NOTHING;
    """)
    with engine.begin() as conn:
        conn.execute(sql)

def load_fact_transactions(engine):
    logger.info("Loading fact_transactions from transformed PaySim data")
    sql = text("""
    INSERT INTO fact_transactions (
        customer_key,
        account_key,
        date_key,
        transaction_type_key,
        amount,
        balance_before,
        balance_after,
        is_fraud,
        is_flagged_fraud,
        hour_of_day
    )
    SELECT
        dc.customer_key,
        da.account_key,
        dd.date_key,
        dt.type_key,
        tp.amount,
        tp.balance_before,
        tp.balance_after,
        CASE WHEN tp.is_fraud = 1 THEN TRUE ELSE FALSE END,
        CASE WHEN tp.is_flagged_fraud = 1 THEN TRUE ELSE FALSE END,
        tp.hour_of_day
    FROM transformed_paysim tp
    JOIN dim_customer dc ON dc.customer_id = tp.customer_id
    JOIN dim_account da ON da.account_id = tp.merchant_id
    JOIN dim_date dd ON dd.date_key = tp.date_key
    JOIN dim_transaction_type dt ON dt.transaction_type = tp.type;
    """)
    with engine.begin() as conn:
        conn.execute(sql)

def create_warehouse_schema(engine):
    """Execute DDL scripts to ensure warehouse dimension and fact tables exist."""
    logger.info("Ensuring warehouse schema (dimensions and fact tables) exists")
    import pathlib
    base_path = pathlib.Path(__file__).resolve().parent.parent.parent
    dim_sql_path = base_path / "sql" / "warehouse" / "create_dimensions.sql"
    fact_sql_path = base_path / "sql" / "warehouse" / "create_fact.sql"

    with engine.begin() as conn:
        if dim_sql_path.exists():
            conn.exec_driver_sql(dim_sql_path.read_text())
        if fact_sql_path.exists():
            conn.exec_driver_sql(fact_sql_path.read_text())

def create_marts_views(engine):
    """Execute marts DDL scripts to create or replace analytical views."""
    logger.info("Creating / refreshing analytical marts views")
    import pathlib
    base_path = pathlib.Path(__file__).resolve().parent.parent.parent
    marts_dir = base_path / "sql" / "marts"
    if marts_dir.exists():
        with engine.begin() as conn:
            for sql_file in marts_dir.glob("*.sql"):
                logger.info("Executing %s", sql_file.name)
                conn.exec_driver_sql(sql_file.read_text())

def main():
    engine = load_db_engine("config/db.yaml")
    create_warehouse_schema(engine)
    populate_dim_customer(engine)
    populate_dim_account(engine)
    populate_dim_date(engine)
    populate_dim_transaction_type(engine)
    load_fact_transactions(engine)
    create_marts_views(engine)
    logger.info("Warehouse loading and marts creation completed.")

if __name__ == "__main__":
    main()
