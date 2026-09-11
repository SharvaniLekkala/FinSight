-- Fact table DDL for FinSight data warehouse

-- Fact transaction table (grain: one row per transaction after cleaning)
CREATE TABLE IF NOT EXISTS fact_transactions (
    transaction_id SERIAL PRIMARY KEY,
    customer_key INT REFERENCES dim_customer(customer_key),
    account_key INT REFERENCES dim_account(account_key),
    date_key INT REFERENCES dim_date(date_key),
    transaction_type_key INT REFERENCES dim_transaction_type(type_key),
    amount NUMERIC,
    balance_before NUMERIC,
    balance_after NUMERIC,
    is_fraud BOOLEAN,
    is_flagged_fraud BOOLEAN,
    hour_of_day INT,
    -- additional columns can be added as needed
    CONSTRAINT fk_customer FOREIGN KEY (customer_key) REFERENCES dim_customer(customer_key),
    CONSTRAINT fk_account FOREIGN KEY (account_key) REFERENCES dim_account(account_key),
    CONSTRAINT fk_date FOREIGN KEY (date_key) REFERENCES dim_date(date_key),
    CONSTRAINT fk_type FOREIGN KEY (transaction_type_key) REFERENCES dim_transaction_type(type_key)
);
