"""
load_from_pipeline.py

Real ETL: reads raw request_logs from Layer 1's tpa_logs.db,
transforms into the star schema, and loads into tpa.db.

See docs/field_mapping.md for the complete data contract.

Idempotent - drops and recreates target tables on every run.
"""

import sqlite3
from pathlib import Path


# -------------------- Config --------------------
RAW_DB = "data/raw/tpa_logs.db"
TARGET_DB = "data/tpa.db"
SCHEMA_PATH = "sql/schema.sql"


# -------------------- Extract --------------------
def extract_raw_logs(raw_db_path):
    """Read all rows from the pipeline's request_logs table."""
    if not Path(raw_db_path).exists():
        raise FileNotFoundError(
            f"Raw pipeline DB not found at {raw_db_path}. "
            "Run Layer 1 (tpa_pipeline_final.py) first, then copy tpa_logs.db into data/raw/."
        )

    conn = sqlite3.connect(raw_db_path)
    conn.row_factory = sqlite3.Row
    rows = conn.execute("SELECT * FROM request_logs").fetchall()
    conn.close()
    print(f"Extracted {len(rows)} rows from {raw_db_path}")
    return rows


# -------------------- Transform --------------------
def build_departments(rows):
    """Extract unique departments into dimension table."""
    unique_names = sorted({r["department"] for r in rows})
    return [
        {
            "department_id": i + 1,
            "department_name": name,
            "cost_center": f"CC{1000 + i + 1}",
        }
        for i, name in enumerate(unique_names)
    ]


def build_users(rows, departments):
    """Extract unique users, link them to department_id via FK."""
    dept_name_to_id = {d["department_name"]: d["department_id"] for d in departments}

    seen = {}
    for r in rows:
        username = r["user_id"]
        if username not in seen:
            seen[username] = r["department"]

    return [
        {
            "user_id": i + 1,
            "username": username,
            "department_id": dept_name_to_id[dept_name],
            "role": "Unknown",
        }
        for i, (username, dept_name) in enumerate(sorted(seen.items()))
    ]


def build_audit_events(rows, users, departments):
    """Transform raw rows into audit_events (fact table)."""
    username_to_id = {u["username"]: u["user_id"] for u in users}
    dept_name_to_id = {d["department_name"]: d["department_id"] for d in departments}

    events = []
    for r in rows:
        events.append({
            "event_id": r["id"],
            "event_timestamp": r["timestamp"],
            "user_id": username_to_id[r["user_id"]],
            "department_id": dept_name_to_id[r["department"]],
            "pii_detected": 1 if r["pii_count"] > 0 else 0,
            "routing_decision": r["action"],
            "prompt_tokens": r["input_tokens"] or 0,
            "response_tokens": r["output_tokens"] or 0,
            "cost_usd": r["cost_usd"] or 0.0,
        })
    return events


def build_pii_events(rows):
    """Split comma-separated pii_detected strings into child rows."""
    pii_events = []
    pii_event_id = 1
    for r in rows:
        pii_text = (r["pii_detected"] or "").strip()
        if not pii_text or pii_text.lower() == "none":
            continue
        for pii_type in [p.strip() for p in pii_text.split(",") if p.strip()]:
            pii_events.append({
                "pii_event_id": pii_event_id,
                "event_id": r["id"],
                "pii_type": pii_type,
                "matched_text": "[REDACTED]",
            })
            pii_event_id += 1
    return pii_events


# -------------------- Load --------------------
def create_schema(conn):
    """Drop and recreate all target tables."""
    conn.executescript("""
        DROP TABLE IF EXISTS pii_events;
        DROP TABLE IF EXISTS audit_events;
        DROP TABLE IF EXISTS users;
        DROP TABLE IF EXISTS departments;
    """)
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        conn.executescript(f.read())
    conn.commit()


def load_table(conn, table, rows, columns):
    """Insert dict rows into the named table."""
    if not rows:
        print(f"  No rows for {table}")
        return
    placeholders = ",".join(["?"] * len(columns))
    col_list = ",".join(columns)
    sql = f"INSERT INTO {table} ({col_list}) VALUES ({placeholders})"
    data = [tuple(row[col] for col in columns) for row in rows]
    conn.executemany(sql, data)
    conn.commit()
    print(f"  Loaded {len(data):>4} rows into {table}")


# -------------------- Main --------------------
if __name__ == "__main__":
    Path("data").mkdir(parents=True, exist_ok=True)

    raw_rows = extract_raw_logs(RAW_DB)

    departments = build_departments(raw_rows)
    users = build_users(raw_rows, departments)
    audit_events = build_audit_events(raw_rows, users, departments)
    pii_events = build_pii_events(raw_rows)

    conn = sqlite3.connect(TARGET_DB)
    conn.execute("PRAGMA foreign_keys = ON;")
    create_schema(conn)

    print("\nLoading into target schema:")
    load_table(conn, "departments", departments,
               ["department_id", "department_name", "cost_center"])
    load_table(conn, "users", users,
               ["user_id", "username", "department_id", "role"])
    load_table(conn, "audit_events", audit_events,
               ["event_id", "event_timestamp", "user_id", "department_id",
                "pii_detected", "routing_decision", "prompt_tokens",
                "response_tokens", "cost_usd"])
    load_table(conn, "pii_events", pii_events,
               ["pii_event_id", "event_id", "pii_type", "matched_text"])

    print("\nFinal row counts:")
    for tbl in ["departments", "users", "audit_events", "pii_events"]:
        count = conn.execute(f"SELECT COUNT(*) FROM {tbl}").fetchone()[0]
        print(f"  {tbl:<15} {count}")

    conn.close()
    print(f"\nETL complete. Analytics DB: {TARGET_DB}")