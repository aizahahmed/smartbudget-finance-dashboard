-- SmartBudget Finance Analytics
-- SQLite database schema and analysis queries

DROP TABLE IF EXISTS transactions;

CREATE TABLE transactions (
    transaction_id TEXT PRIMARY KEY,
    transaction_date DATE NOT NULL,
    department TEXT NOT NULL,
    category TEXT NOT NULL,
    vendor TEXT NOT NULL,
    budget NUMERIC NOT NULL CHECK (budget >= 0),
    actual NUMERIC NOT NULL CHECK (actual >= 0),
    status TEXT NOT NULL,
    payment_method TEXT NOT NULL
);

CREATE INDEX idx_department
ON transactions(department);

CREATE INDEX idx_category
ON transactions(category);

CREATE INDEX idx_transaction_date
ON transactions(transaction_date);

-- Company budget summary
SELECT
    ROUND(SUM(budget), 2) AS total_budget,
    ROUND(SUM(actual), 2) AS total_actual,
    ROUND(SUM(budget) - SUM(actual), 2) AS variance,
    ROUND(
        100.0 * SUM(actual) / NULLIF(SUM(budget), 0),
        1
    ) AS budget_used_percent
FROM transactions;

-- Spending by department
SELECT
    department,
    ROUND(SUM(budget), 2) AS total_budget,
    ROUND(SUM(actual), 2) AS total_actual,
    ROUND(SUM(budget) - SUM(actual), 2) AS variance,
    CASE
        WHEN SUM(actual) > SUM(budget)
            THEN 'Over budget'
        ELSE 'Within budget'
    END AS budget_status
FROM transactions
GROUP BY department
ORDER BY total_actual DESC;

-- Spending by category
SELECT
    category,
    ROUND(SUM(budget), 2) AS total_budget,
    ROUND(SUM(actual), 2) AS total_actual,
    ROUND(SUM(actual) - SUM(budget), 2) AS overspending,
    ROUND(
        100.0 * (SUM(actual) - SUM(budget))
        / NULLIF(SUM(budget), 0),
        1
    ) AS variance_percent
FROM transactions
GROUP BY category
ORDER BY overspending DESC;

-- Ten largest transactions
SELECT
    transaction_id,
    transaction_date,
    department,
    category,
    vendor,
    budget,
    actual,
    actual - budget AS amount_over_budget
FROM transactions
ORDER BY actual DESC
LIMIT 10;

-- Monthly spending trend
SELECT
    STRFTIME('%Y-%m', transaction_date) AS month,
    ROUND(SUM(budget), 2) AS total_budget,
    ROUND(SUM(actual), 2) AS total_actual,
    ROUND(SUM(budget) - SUM(actual), 2) AS variance
FROM transactions
GROUP BY STRFTIME('%Y-%m', transaction_date)
ORDER BY month;

-- Vendors with repeated overspending
SELECT
    vendor,
    COUNT(*) AS transaction_count,
    SUM(
        CASE WHEN actual > budget THEN 1 ELSE 0 END
    ) AS over_budget_count,
    ROUND(SUM(actual - budget), 2) AS net_amount_over_budget
FROM transactions
GROUP BY vendor
HAVING SUM(
    CASE WHEN actual > budget THEN 1 ELSE 0 END
) >= 2
ORDER BY net_amount_over_budget DESC;

-- Transactions more than 25 percent over budget
SELECT
    transaction_id,
    department,
    category,
    vendor,
    budget,
    actual,
    ROUND(
        100.0 * (actual - budget) / NULLIF(budget, 0),
        1
    ) AS over_budget_percent
FROM transactions
WHERE actual > budget * 1.25
ORDER BY over_budget_percent DESC;
