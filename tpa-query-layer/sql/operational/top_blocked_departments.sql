-- BUSINESS QUESTION:
-- Which departments have the highest governance-intervention rate?
-- WHY IT MATTERS:
-- Departments with higher block rates may need targeted training,
-- stricter rules, or a review of their AI use cases.

SELECT
    d.department_name,
    COUNT(*) AS total_events,
    SUM(CASE WHEN a.routing_decision = 'BLOCKED' THEN 1 ELSE 0 END) AS blocked_count,
    ROUND(
        100.0 * SUM(CASE WHEN a.routing_decision = 'BLOCKED' THEN 1 ELSE 0 END)
        / COUNT(*),
        2
    ) AS block_rate_pct
FROM audit_events a
JOIN departments d ON a.department_id = d.department_id
GROUP BY d.department_name
ORDER BY blocked_count DESC
LIMIT 5;
