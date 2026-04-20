-- VALIDATION CHECK:
-- A CLEARED event (which hit the API) must have a positive cost.
-- BLOCKED events should have cost = 0 (never sent to API).
-- Non-positive cost on a CLEARED event indicates a calculation bug.
-- EXPECTED RESULT: 0 rows.

SELECT
    event_id,
    routing_decision,
    prompt_tokens,
    response_tokens,
    cost_usd
FROM audit_events
WHERE routing_decision = 'CLEARED'
  AND cost_usd <= 0;