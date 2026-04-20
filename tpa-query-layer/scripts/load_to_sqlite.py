"""
load_to_sqlite.py

Creates the TPA schema in SQLite and loads the 4 CSVs produced by
generate_data.py into the proper tables in FK-safe order.

Run AFTER generate_data.py.
"""

import csv
import sqlite3
from pathlib import Path


# -------------------- Config --------------------
DB_PATH = "data/tpa.db"
SCHEMA_PATH = "sql/schema.sql"
RAW_DIR = "data/raw"


# -------------------- Functions --------------------
def create_schema(conn):
    """Drop existing tables (if any) and execute schema.sql."""

    # Drop in reverse FK order so constraints don't complain
    cur = conn.cursor()
    cur.executescript("""
        DROP TABLE IF EXISTS pii_events;
        DROP TABLE IF EXISTS audit_events;
        DROP TABLE IF EXISTS users;
        DROP TABLE IF EXISTS departments;
    """)

    # Read schema file and execute all CREATE TABLE statements at once
    with open(SCHEMA_PATH, "r") as f:
        schema_sql = f.read()
    cur.executescript(schema_sql)
    conn.commit()
    print("Schema created.")


def load_csv(conn, table_name, csv_path, columns):
    """
    Read a CSV and insert its rows into the given table.
    `columns` is a list of column names matching CSV headers AND the table.
    """
    cur = conn.cursor()

    # Build the parameterized INSERT statement dynamically
    placeholders = ",".join(["?"] * len(columns))
    col_list = ",".join(columns)
    sql = f"INSERT INTO {table_name} ({col_list}) VALUES ({placeholders})"

    # Read the CSV and build the list of tuples for executemany
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = [tuple(row[col] for col in columns) for row in reader]

    cur.executemany(sql, rows)
    conn.commit()
    print(f"Loaded {len(rows):>5} rows into {table_name}")


# -------------------- Main --------------------
if __name__ == "__main__":
    Path("data").mkdir(exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")   # enforce FK integrity

    create_schema(conn)

    # Load order matters (parents before children)
    load_csv(
        conn,
        "departments",
        f"{RAW_DIR}/departments.csv",
        ["department_id", "department_name", "cost_center"],
    )
    load_csv(
        conn,
        "users",
        f"{RAW_DIR}/users.csv",
        ["user_id", "username", "department_id", "role"],
    )
    load_csv(
        conn,
        "audit_events",
        f"{RAW_DIR}/audit_events.csv",
        [
            "event_id",
            "event_timestamp",
            "user_id",
            "department_id",
            "pii_detected",
            "routing_decision",
            "prompt_tokens",
            "response_tokens",
            "cost_usd",
        ],
    )
    load_csv(
        conn,
        "pii_events",
        f"{RAW_DIR}/pii_events.csv",
        ["pii_event_id", "event_id", "pii_type", "matched_text"],
    )

    # Quick sanity check
    cur = conn.cursor()
    print("\nRow counts:")
    for tbl in ["departments", "users", "audit_events", "pii_events"]:
        count = cur.execute(f"SELECT COUNT(*) FROM {tbl}").fetchone()[0]
        print(f"  {tbl:<15} {count}")

    conn.close()
    print("\nLoad complete. DB saved to", DB_PATH)
