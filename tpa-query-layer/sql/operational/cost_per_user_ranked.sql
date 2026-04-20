-- BUSINESS QUESTION:
-- Who are the highest-spend users, and how does each compare
-- to the average user spend?
-- TECHNIQUE:
-- Window functions (RANK and AVG OVER) add per-row rankings
-- without collapsing the result set via GROUP BY.

SELECT
    u.username,
    d.department_name,
    ROUND(SUM(a.cost_usd), 4) AS total_cost,
    RANK() OVER (ORDER BY SUM(a.cost_usd) DESC) AS spend_rank,
    ROUND(AVG(SUM(a.cost_usd)) OVER (), 4) AS avg_user_cost
FROM audit_events a
JOIN users u ON a.user_id = u.user_id
JOIN departments d ON a.department_id = d.department_id
GROUP BY u.username, d.department_name
ORDER BY spend_rank
LIMIT 20;
