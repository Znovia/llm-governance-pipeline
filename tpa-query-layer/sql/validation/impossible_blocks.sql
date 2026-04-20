-- VALIDATION CHECK:
-- A BLOCKED event must always have pii_detected = 1.
-- If any rows return, the pipeline is producing logically
-- inconsistent data and needs investigation.
-- EXPECTED RESULT: 0 rows.

SELECT
    event_id,
    routing_decision,
    pii_detected
FROM audit_events
WHERE routing_decision = 'BLOCKED'
  AND pii_detected = 0;
