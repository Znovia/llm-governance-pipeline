SELECT
    DATE(event_timestamp) AS event_date,
    COUNT(*) AS total_requests,
    SUM(prompt_tokens + response_tokens) AS total_tokens,
    ROUND(SUM(cost_usd), 2) AS total_cost
FROM audit_events
GROUP BY event_date
ORDER BY event_date DESC;
