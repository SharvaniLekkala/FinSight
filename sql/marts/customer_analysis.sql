-- Customer analysis view
CREATE OR REPLACE VIEW vw_customer_transactions AS
SELECT
    c.customer_key,
    c.customer_id,
    COUNT(f.transaction_id) AS txn_count,
    SUM(f.amount) AS total_amount,
    AVG(f.amount) AS avg_amount,
    SUM(CASE WHEN f.is_fraud THEN 1 ELSE 0 END) AS fraud_txn_count,
    SUM(CASE WHEN NOT f.is_fraud THEN 1 ELSE 0 END) AS legit_txn_count
FROM dim_customer c
LEFT JOIN fact_transactions f ON f.customer_key = c.customer_key
GROUP BY c.customer_key, c.customer_id
ORDER BY total_amount DESC;
