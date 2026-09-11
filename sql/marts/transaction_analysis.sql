-- Transaction analysis view
CREATE OR REPLACE VIEW vw_transaction_summary AS
SELECT
    d.date_key,
    d.date,
    tt.transaction_type,
    COUNT(*) AS txn_count,
    SUM(f.amount) AS total_amount,
    AVG(f.amount) AS avg_amount
FROM fact_transactions f
JOIN dim_date d ON f.date_key = d.date_key
JOIN dim_transaction_type tt ON f.transaction_type_key = tt.type_key
GROUP BY d.date_key, d.date, tt.transaction_type
ORDER BY d.date_key;
