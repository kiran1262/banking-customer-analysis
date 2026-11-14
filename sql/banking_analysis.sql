-- Banking Customer Analysis starter SQL. Adapt names to your database.
-- 1. Overall KPIs
SELECT COUNT(*) AS total_transactions,
       COUNT(DISTINCT customer_id) AS unique_customers,
       SUM(amount) AS total_value, AVG(amount) AS average_value
FROM banking_transactions;

-- 2. Monthly trend (PostgreSQL syntax)
SELECT DATE_TRUNC('month', transaction_date) AS month,
       COUNT(*) AS transactions, SUM(amount) AS transaction_value
FROM banking_transactions
GROUP BY 1 ORDER BY 1;

-- 3. Customer activity
SELECT customer_id, COUNT(*) AS transactions,
       SUM(amount) AS lifetime_value, AVG(amount) AS average_value
FROM banking_transactions
GROUP BY customer_id ORDER BY lifetime_value DESC;

-- 4. Transaction type / channel mix
SELECT transaction_type, COUNT(*) AS transactions, SUM(amount) AS value
FROM banking_transactions GROUP BY transaction_type ORDER BY value DESC;

-- 5. Success rate by channel
SELECT channel, COUNT(*) AS total_transactions,
       SUM(CASE WHEN LOWER(status) IN ('success','completed','settled') THEN 1 ELSE 0 END) AS successful
FROM banking_transactions GROUP BY channel;
