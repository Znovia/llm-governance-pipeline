"""
run_query.py

Run any .sql file against the analytics database and print results.

Usage:
    python scripts/run_query.py sql/risk_quality/cost_outliers.sql
"""

import sys
import sqlite3
from pathlib import Path


DB_PATH = "data/tpa.db"


def run_query(sql_path):
    path = Path(sql_path)
    if not path.exists():
        print(f"ERROR: SQL file not found: {sql_path}")
        sys.exit(1)

    with open(path, "r", encoding="utf-8") as f:
        query = f.read()

    conn = sqlite3.connect(DB_PATH)
    try:
        cur = conn.cursor()
        cur.execute(query)
        rows = cur.fetchall()
        headers = [d[0] for d in cur.description] if cur.description else []
    finally:
        conn.close()

    # Header — use the SQL filename
    print(f"\n{path.stem.upper().replace('_', ' ')}")
    print("=" * 90)

    if not headers:
        print("(query returned no columns)")
        return

    # Print column headers
    col_widths = [max(len(str(h)), 12) for h in headers]
    header_line = "  ".join(f"{h:<{w}}" for h, w in zip(headers, col_widths))
    print(header_line)
    print("-" * 90)

    # Print rows
    if not rows:
        print("(no rows returned)")
    else:
        for row in rows:
            values = [str(v) if v is not None else "NULL" for v in row]
            line = "  ".join(f"{v:<{w}}" for v, w in zip(values, col_widths))
            print(line)

    print(f"\n{len(rows)} row(s) returned")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python scripts/run_query.py <path/to/query.sql>")
        sys.exit(1)
    run_query(sys.argv[1])