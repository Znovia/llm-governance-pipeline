-- BUSINESS QUESTION:
-- Which users show a pattern of repeated governance violations
-- in the last 7 days?
-- TECHNIQUE:
-- HAVING filters groups AFTER aggregation. A WHERE clause cannot
-- filter on COUNT(*) — only HAVING can.

SELECT
    u.username,
    d.department_name,
    COUNT(*) AS blocked_count
FROM audit_events a
JOIN users u ON a.user_id = u.user_id
JOIN departments d ON a.department_id = d.department_id
WHERE a.routing_decision = 'BLOCKED'
  AND a.event_timestamp >= datetime('now', '-7 days')
GROUP BY u.username, d.department_name
HAVING COUNT(*) > 3
ORDER BY blocked_count DESC;
