-- BUSINESS QUESTION:
-- Is the PII detection rate trending up or down compared to
-- the previous month?
-- TECHNIQUE:
-- LAG() window function pulls a value from the previous row
-- so the current row can compute a delta.

WITH monthly AS (
    SELECT
        strftime('%Y-%m', event_timestamp) AS month,
        COUNT(*) AS total_events,
        ROUND(100.0 * SUM(pii_detected) / COUNT(*), 2) AS pii_rate_pct
    FROM audit_events
    GROUP BY month
)
SELECT
    month,
    total_events,
    pii_rate_pct,
    LAG(pii_rate_pct) OVER (ORDER BY month) AS prev_month_rate,
    ROUND(pii_rate_pct - LAG(pii_rate_pct) OVER (ORDER BY month), 2) AS delta
FROM monthly
ORDER BY month;
