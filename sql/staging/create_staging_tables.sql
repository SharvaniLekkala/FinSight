-- Staging table DDL for FinSight
-- Note: These tables are auto-created by pandas to_sql() during ingestion.
-- This file is provided as reference documentation for the expected schemas.

-- PaySim staging table
CREATE TABLE IF NOT EXISTS stg_paysim_raw (
    step INT,
    type TEXT,
    amount NUMERIC,
    "nameOrig" TEXT,
    "oldbalanceOrg" NUMERIC,
    "newbalanceOrig" NUMERIC,
    "nameDest" TEXT,
    "oldbalanceDest" NUMERIC,
    "newbalanceDest" NUMERIC,
    "isFraud" INT,
    "isFlaggedFraud" INT
);

-- UCI Credit Card Default staging table
CREATE TABLE IF NOT EXISTS stg_credit_raw (
    "ID" INT,
    "LIMIT_BAL" NUMERIC,
    "SEX" INT,
    "EDUCATION" INT,
    "MARRIAGE" INT,
    "AGE" INT,
    "PAY_0" INT,
    "PAY_2" INT,
    "PAY_3" INT,
    "PAY_4" INT,
    "PAY_5" INT,
    "PAY_6" INT,
    "BILL_AMT1" NUMERIC,
    "BILL_AMT2" NUMERIC,
    "BILL_AMT3" NUMERIC,
    "BILL_AMT4" NUMERIC,
    "BILL_AMT5" NUMERIC,
    "BILL_AMT6" NUMERIC,
    "PAY_AMT1" NUMERIC,
    "PAY_AMT2" NUMERIC,
    "PAY_AMT3" NUMERIC,
    "PAY_AMT4" NUMERIC,
    "PAY_AMT5" NUMERIC,
    "PAY_AMT6" NUMERIC,
    "default.payment.next.month" INT
);
