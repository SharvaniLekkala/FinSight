import logging
from sqlalchemy import create_engine, text
import pandas as pd
from src.ingestion.loader import load_db_engine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def populate_dim_customer(engine):
    logger.info("Populating dim_customer from transformed tables")
    # Union distinct customers from both datasets
    sql = """
    INSERT INTO dim_customer (customer_id, gender, education, marriage, age, age_group)
    SELECT DISTINCT customer_id,
        COALESCE(sex, gender) AS gender,
        COALESCE(education, education) AS education,
        COALESCE(marriage, marriage) AS marriage,
        COALESCE(age, age) AS age,
        COALESCE(age_group, age_group) AS age_group
    FROM (
        SELECT customer_id, NULL::TEXT AS gender, NULL::TEXT AS education, NULL::TEXT AS marriage,
               NULL::INT AS age, NULL::TEXT AS age_group FROM transformed_paysim
        UNION ALL
        SELECT customer_id, sex AS gender, education, marriage, age, age_group FROM transformed_credit
    ) AS u;
    """
    engine.execute(text(sql))

def populate_dim_account(engine):
    logger.info("Populating dim_account from PaySim data")
    sql = """
    INSERT INTO dim_account (account_id)
    SELECT DISTINCT merchant_id FROM transformed_paysim;
    """
    engine.execute(text(sql))

def populate_dim_date(engine):
    logger.info("Populating dim_date from transformed PaySim data (transaction timestamps)")
    sql = """
    INSERT INTO dim_date (date_key, date, year, month, day, weekday)
    SELECT DISTINCT date_key,
        DATE_TRUNC('day', transaction_timestamp)::DATE AS date,
        EXTRACT(YEAR FROM transaction_timestamp)::INT AS year,
        EXTRACT(MONTH FROM transaction_timestamp)::INT AS month,
        EXTRACT(DAY FROM transaction_timestamp)::INT AS day,
        EXTRACT(DOW FROM transaction_timestamp)::INT AS weekday
    FROM transformed_paysim;
    """
    engine.execute(text(sql))

def populate_dim_transaction_type(engine):
    logger.info("Populating dim_transaction_type from PaySim type codes")
    sql = """
    INSERT INTO dim_transaction_type (transaction_type, description)
    SELECT DISTINCT type, NULL FROM transformed_paysim;
    """
    engine.execute(text(sql))

def load_fact_transactions(engine):
    logger.info("Loading fact_transactions from transformed PaySim data")
    sql = """
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
        tp.is_fraud,
        tp.is_flagged_fraud,
        tp.hour_of_day
    FROM transformed_paysim tp
    JOIN dim_customer dc ON dc.customer_id = tp.customer_id
    JOIN dim_account da ON da.account_id = tp.merchant_id
    JOIN dim_date dd ON dd.date_key = tp.date_key
    JOIN dim_transaction_type dt ON dt.transaction_type = tp.type;
    """
    engine.execute(text(sql))

def main():
    engine = load_db_engine("config/db.yaml")
    # Ensure dimensions exist (run dimension DDLs beforehand)
    populate_dim_customer(engine)
    populate_dim_account(engine)
    populate_dim_date(engine)
    populate_dim_transaction_type(engine)
    load_fact_transactions(engine)
    logger.info("Warehouse loading completed.")

if __name__ == "__main__":
    main()
