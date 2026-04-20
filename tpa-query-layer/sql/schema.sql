-- ==================================================================
-- TPA Query Layer Schema
-- Star schema: audit_events (fact) + users, departments, pii_events
-- ==================================================================

-- Dimension: departments
CREATE TABLE departments (
    department_id   INTEGER PRIMARY KEY,
    department_name TEXT NOT NULL UNIQUE,
    cost_center     TEXT NOT NULL
);

-- Dimension: users
CREATE TABLE users (
    user_id       INTEGER PRIMARY KEY,
    username      TEXT    NOT NULL,
    department_id INTEGER NOT NULL,
    role          TEXT    NOT NULL,
    FOREIGN KEY (department_id) REFERENCES departments(department_id)
);

-- Fact: audit_events (grain = one LLM prompt event)
CREATE TABLE audit_events (
    event_id         INTEGER PRIMARY KEY,
    event_timestamp  TEXT    NOT NULL,
    user_id          INTEGER NOT NULL,
    department_id    INTEGER NOT NULL,
    pii_detected     INTEGER NOT NULL,
    routing_decision TEXT    NOT NULL,
    prompt_tokens    INTEGER NOT NULL,
    response_tokens  INTEGER NOT NULL,
    cost_usd         REAL    NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (department_id) REFERENCES departments(department_id)
);

-- Child: pii_events (one-to-many with audit_events)
CREATE TABLE pii_events (
    pii_event_id INTEGER PRIMARY KEY,
    event_id     INTEGER NOT NULL,
    pii_type     TEXT    NOT NULL,
    matched_text TEXT,
    FOREIGN KEY (event_id) REFERENCES audit_events(event_id)
);

-- Indexes for query performance
CREATE INDEX idx_audit_user ON audit_events(user_id);
CREATE INDEX idx_audit_dept ON audit_events(department_id);
CREATE INDEX idx_audit_ts   ON audit_events(event_timestamp);
CREATE INDEX idx_pii_event  ON pii_events(event_id);
