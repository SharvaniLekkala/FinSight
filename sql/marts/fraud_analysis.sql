-- Fraud risk analysis view
CREATE OR REPLACE VIEW vw_fraud_summary AS
SELECT
    d.date_key,
    d.date,
    COUNT(*) FILTER (WHERE f.is_fraud) AS fraud_txn_count,
    COUNT(*) FILTER (WHERE NOT f.is_fraud) AS legit_txn_count,
    SUM(f.amount) FILTER (WHERE f.is_fraud) AS fraud_total_amount,
    SUM(f.amount) FILTER (WHERE NOT f.is_fraud) AS legit_total_amount,
    AVG(f.amount) FILTER (WHERE f.is_fraud) AS fraud_avg_amount,
    AVG(f.amount) FILTER (WHERE NOT f.is_fraud) AS legit_avg_amount
FROM fact_transactions f
JOIN dim_date d ON f.date_key = d.date_key
GROUP BY d.date_key, d.date
ORDER BY d.date_key;
