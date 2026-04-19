import os
import re
import sqlite3

from datetime import datetime
from dotenv import load_dotenv

import anthropic


load_dotenv()
api_key = os.getenv("API_KEY")

db_file = "tpa_logs.db"

conn = sqlite3.connect(db_file)
cursor = conn.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS request_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT, user_id TEXT, department TEXT,
        use_case TEXT, original_input TEXT, pii_detected TEXT,
        pii_count INTEGER, action TEXT, input_tokens INTEGER,
        output_tokens INTEGER, total_tokens INTEGER,
        cost_usd REAL, ai_response TEXT
    )
""")
conn.commit()
conn.close()

MODEL     = "claude-sonnet-4-6"
client    = anthropic.Anthropic(api_key=api_key)


COST_IN   = 3.00   # $ per 1M input tokens
COST_OUT  = 15.00  # $ per 1M output tokens



mock_requests = [
    
    {"user_id": "A123", "department": "Accounting",  "use_case": "Loan summary",
     "message": "Summarize john loan application. 492-11-882, email john@gmail.com, 562-985-6425"},

    {"user_id": "D321", "department": "Compliance",  "use_case": "Policy check",
     "message": "Is sharing customer account number 88291-4421 with a third party vendor allowed?"},

    {"user_id": "E654", "department": "Accounting",  "use_case": "Invoice review",
     "message": "Review this invoice 04960. Vendor bank account 291-881-5555 routing number 021000021-995"},


]


def scan_for_pii(text):
    """
    Scan text for common PII patterns.
    Returns a list of human-readable labels for each match found.
    """
    pii_found = []

   
    if re.search(r'\b\d{3}-\d{2}-\d{4}\b', text):
        pii_found.append("SSN")

  
    if re.search(r'\b[\w.-]+@[\w.-]+\.\w+\b', text):
        pii_found.append("Email")

  
    if re.search(r'\(?\d{3}\)?[\s.-]\d{3}[\s.-]\d{4}', text):
        pii_found.append("Phone")

    
    if re.search(r'\b\d{4}[\s-]\d{4}[\s-]\d{4}[\s-]\d{4}\b', text):
        pii_found.append("Credit card")

    if re.search(r'\b\d{3}-\d{3}-\d{4}\b', text):
        pii_found.append("Bank account")
    if re.search(r'\brouting\s+number\b', text, re.IGNORECASE):
        pii_found.append("Routing number")


    if re.search(r'account\s+number[\s:]+[\d-]+', text, re.IGNORECASE):
        pii_found.append("Account number")

    return pii_found



def log_to_sqlite(user_id, department, use_case, original_input,
                  pii_found, action,
                  input_tokens=0, output_tokens=0,
                  cost_usd=0.0, ai_response=None):
    """
    Write one pipeline result to the database.
    Works for both BLOCKED and CLEARED requests.
    """
    conn   = sqlite3.connect(db_file)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO request_logs (
            timestamp, user_id, department, use_case,
            original_input, pii_detected, pii_count,
            action, input_tokens, output_tokens, total_tokens,
            cost_usd, ai_response
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        user_id, department, use_case,
        original_input,
        ", ".join(pii_found) if pii_found else "none",
        len(pii_found),
        action,
        input_tokens,
        output_tokens,
        input_tokens + output_tokens,
        round(cost_usd, 6),
        ai_response if ai_response else "BLOCKED — not sent to AI",
    ))

    conn.commit()
    conn.close()


for request in mock_requests:
    user_id    = request["user_id"]
    department = request["department"]
    use_case   = request["use_case"]
    user_input = request["message"]

    
    pii_found = scan_for_pii(user_input)

    
    if pii_found:
    
        action        = "BLOCKED"
        input_tokens  = 0
        output_tokens = 0
        cost_usd      = 0.0
        ai_response   = None

        log_to_sqlite(
            user_id, department, use_case, user_input,
            pii_found, action,
            input_tokens, output_tokens, cost_usd, ai_response
        )


    else:
        
        action = "CLEARED"

        resp = client.messages.create(
            model=MODEL,
            max_tokens=256,
            messages=[{"role": "user", "content": user_input}]
        )

        ai_response   = resp.content[0].text
        input_tokens  = resp.usage.input_tokens
        output_tokens = resp.usage.output_tokens
        cost_usd      = (input_tokens / 1_000_000) * COST_IN + \
                        (output_tokens / 1_000_000) * COST_OUT

        log_to_sqlite(
            user_id, department, use_case, user_input,
            pii_found, action,
            input_tokens, output_tokens, cost_usd, ai_response
        )
# Verify logging worked
conn = sqlite3.connect(db_file)
rows = conn.execute("SELECT user_id, action, pii_detected FROM request_logs").fetchall()
conn.close()

print(f"\n--- PIPELINE RESULTS: {len(rows)} requests logged ---")
for row in rows:
    print(row)