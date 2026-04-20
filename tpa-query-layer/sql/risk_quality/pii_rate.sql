SELECT
    department_id,
    COUNT(*) AS total_events,
    SUM(pii_detected) AS pii_events,
    ROUND(SUM(pii_detected) * 1.0 / COUNT(*), 3) AS pii_rate
FROM audit_events
GROUP BY department_id
ORDER BY pii_rate DESC;