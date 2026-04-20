-- BUSINESS QUESTION:
-- Are certain PII types more likely to be blocked than others?
-- WHY IT MATTERS:
-- If one PII category (e.g. SSN) is always blocked but another
-- (e.g. EMAIL) sometimes clears, it signals rule inconsistencies
-- or different severity treatments worth reviewing.

SELECT
    p.pii_type,
    COUNT(*) AS total_matches,
    SUM(CASE WHEN a.routing_decision = 'BLOCKED' THEN 1 ELSE 0 END) AS blocked_matches,
    ROUND(
        100.0 * SUM(CASE WHEN a.routing_decision = 'BLOCKED' THEN 1 ELSE 0 END)
        / COUNT(*),
        2
    ) AS block_pct
FROM pii_events p
JOIN audit_events a ON p.event_id = a.event_id
GROUP BY p.pii_type
ORDER BY block_pct DESC;
