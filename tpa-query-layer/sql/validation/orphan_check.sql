SELECT *
FROM audit_events ae
LEFT JOIN users u ON ae.user_id = u.user_id
WHERE u.user_id IS NULL;