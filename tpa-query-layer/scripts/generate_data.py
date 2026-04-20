import random
import csv
from pathlib import Path
from faker import Faker
from datetime import datetime, timedelta

fake = Faker()
random.seed(42)


def generate_departments(n=15):
    department_names = [
        "Finance",
        "HR",
        "Legal",
        "Compliance",
        "IT",
        "Security",
        "Sales",
        "Operations",
        "Marketing",
        "Procurement",
        "Risk",
        "Engineering",
        "Customer Success",
        "Public Relations",
        "Research and Development",
    ]

    departments = []

    for i in range(n):
        dept = {
            "department_id": i + 1,
            "department_name": department_names[i],
            "cost_center": f"CC{1000 + i + 1}"
        }
        departments.append(dept)

    return departments


def generate_users(n=75, departments=None):
    users = []

    for i in range(n):
        dept = random.choice(departments)

        user = {
            "user_id": i + 1,
            "username": fake.user_name(),
            "department_id": dept["department_id"],
            "role": random.choice(["Analyst", "Manager", "Associate"])
        }

        users.append(user)

    return users


def generate_audit_events(n=1000, users=None):
    events = []

    for i in range(n):
        user = random.choice(users)

        if random.random() < 0.85:
            routing_decision = "CLEARED"
            pii_detected = 0
        else:
            routing_decision = "BLOCKED"
            pii_detected = 1

        prompt_tokens = random.randint(10, 500)
        response_tokens = random.randint(50, 2000)
        cost_usd = (prompt_tokens * 0.000003) + (response_tokens * 0.000015)

        event_time = datetime.now() - timedelta(days=random.randint(0, 90))

        event = {
            "event_id": i + 1,
            "event_timestamp": event_time.isoformat(),
            "user_id": user["user_id"],
            "department_id": user["department_id"],
            "pii_detected": pii_detected,
            "routing_decision": routing_decision,
            "prompt_tokens": prompt_tokens,
            "response_tokens": response_tokens,
            "cost_usd": round(cost_usd, 6)
        }

        events.append(event)

    return events


def generate_pii_events(audit_events):
    pii_types = ["SSN", "EMAIL", "PHONE", "ACCOUNT"]
    pii_events = []
    pii_event_id = 1

    for event in audit_events:
        if event["routing_decision"] == "BLOCKED":
            num_matches = random.randint(1, 3)

            for _ in range(num_matches):
                pii_event = {
                    "pii_event_id": pii_event_id,
                    "event_id": event["event_id"],
                    "pii_type": random.choice(pii_types),
                    "matched_text": "[REDACTED]"
                }
                pii_events.append(pii_event)
                pii_event_id += 1

    return pii_events


def write_csv(path, rows, headers):
    with open(path, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    Path("data/raw").mkdir(parents=True, exist_ok=True)

    departments = generate_departments()
    users = generate_users(departments=departments)
    audit_events = generate_audit_events(users=users)
    pii_events = generate_pii_events(audit_events)

    write_csv(
        "data/raw/departments.csv",
        departments,
        ["department_id", "department_name", "cost_center"]
    )

    write_csv(
        "data/raw/users.csv",
        users,
        ["user_id", "username", "department_id", "role"]
    )

    write_csv(
        "data/raw/audit_events.csv",
        audit_events,
        [
            "event_id",
            "event_timestamp",
            "user_id",
            "department_id",
            "pii_detected",
            "routing_decision",
            "prompt_tokens",
            "response_tokens",
            "cost_usd"
        ]
    )

    write_csv(
        "data/raw/pii_events.csv",
        pii_events,
        ["pii_event_id", "event_id", "pii_type", "matched_text"]
    )
import sqlite3

conn = sqlite3.connect("data/tpa.db")
cur = conn.cursor()

print("\nCOST OUTLIERS SAMPLE:\n")

query = """
WITH dept_avg AS (
    SELECT
        event_id,
        department_id,
        cost_usd,
        AVG(cost_usd) OVER (PARTITION BY department_id) AS dept_avg_cost
    FROM audit_events
)
SELECT *
FROM dept_avg
WHERE cost_usd > 2 * dept_avg_cost
LIMIT 10;
"""

rows = cur.execute(query).fetchall()

for row in rows:
    print(row)

conn.close()