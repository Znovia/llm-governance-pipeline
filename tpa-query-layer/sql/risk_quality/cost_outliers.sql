-- BUSINESS QUESTION:
-- Which individual prompts cost more than 2x their department's
-- average prompt cost?
-- TECHNIQUES:
-- 1) CTE (WITH clause) for readability
-- 2) Window function AVG OVER PARTITION BY for per-department average
--    without collapsing rows with GROUP BY.
-- THIS IS THE STRONGEST INTERVIEW QUERY — lead with it when asked
-- "show me a SQL query you're proud of".

WITH dept_avg AS (
    SELECT
        a.event_id,
        a.user_id,
        a.department_id,
        a.cost_usd,
        AVG(a.cost_usd) OVER (PARTITION BY a.department_id) AS dept_avg_cost
    FROM audit_events a
)
SELECT
    d.department_name,
    u.username,
    event_id,
    ROUND(cost_usd, 4)       AS cost_usd,
    ROUND(dept_avg_cost, 4)  AS dept_avg_cost,
    ROUND(cost_usd / dept_avg_cost, 2) AS multiple_of_avg
FROM dept_avg
JOIN users u ON dept_avg.user_id = u.user_id
JOIN departments d ON dept_avg.department_id = d.department_id
WHERE cost_usd > 2 * dept_avg_cost
ORDER BY multiple_of_avg DESC
LIMIT 20;
