-- Credit risk analysis view
CREATE OR REPLACE VIEW vw_credit_default_summary AS
SELECT
    c.customer_key,
    c.age_group,
    c.education,
    c.marriage,
    AVG(t.amount) AS avg_transaction_amount,
    SUM(CASE WHEN cr.default_payment_next_month = 1 THEN 1 ELSE 0 END) AS default_count,
    COUNT(*) AS total_customers
FROM dim_customer c
JOIN transformed_credit cr ON c.customer_id = cr.customer_id
LEFT JOIN fact_transactions t ON t.customer_key = c.customer_key
GROUP BY c.customer_key, c.age_group, c.education, c.marriage
ORDER BY c.customer_key;
