-- Dimensions DDL for FinSight data warehouse

-- Customer dimension (derived from transformed data)
CREATE TABLE IF NOT EXISTS dim_customer (
    customer_key SERIAL PRIMARY KEY,
    customer_id TEXT UNIQUE,
    gender TEXT,
    education TEXT,
    marriage TEXT,
    age INT,
    age_group TEXT
);

-- Date dimension
CREATE TABLE IF NOT EXISTS dim_date (
    date_key INT PRIMARY KEY,
    date DATE,
    year INT,
    month INT,
    day INT,
    weekday INT
);

-- Transaction type dimension (type codes from PaySim)
CREATE TABLE IF NOT EXISTS dim_transaction_type (
    type_key SERIAL PRIMARY KEY,
    transaction_type INT UNIQUE,
    description TEXT
);

-- Account dimension (placeholder for accounts in PaySim)
CREATE TABLE IF NOT EXISTS dim_account (
    account_key SERIAL PRIMARY KEY,
    account_id TEXT UNIQUE
);
