# LLM Governance Platform

A data platform for monitoring, controlling, and analyzing LLM request traffic. The system scans prompts for sensitive data (PII), enforces governance rules (BLOCKED vs. CLEARED), logs every request, and exposes a structured analytics layer for downstream analysis.

## Overview

This project combines an ingestion pipeline with a structured query layer to simulate how organizations can safely integrate LLM usage into internal systems.

At a high level, the platform:

- Intercepts LLM prompts before they are processed  
- Detects potential PII using pattern-based validation  
- Applies governance rules to allow or block requests  
- Logs all activity for auditing and cost tracking  
- Transforms raw logs into structured tables for analysis  

## Architecture

The system is organized into two integrated components:

### 1. Ingestion Pipeline (Python)

A Python pipeline that simulates LLM request interception and governance.

**Responsibilities:**

- Scan incoming prompts for PII using regex patterns (SSN, email, phone, account numbers, routing numbers)  
- Classify requests as:
  - `BLOCKED` → PII detected; request never reaches the LLM  
  - `CLEARED` → safe to process; forwarded to the Claude API  
- Capture metadata for each request:
  - prompt text and timestamp  
  - input/output token counts  
  - estimated cost  
  - decision outcome  
- Log every transaction to a SQLite database (`request_logs` table)  

**File:** `tpa_pipeline_final.py`

---

### 2. Query Layer (ETL + SQL Analytics)

Transforms raw pipeline logs into a normalized analytics schema for analysis.

**Responsibilities:**

- ETL process that reads raw `request_logs` and loads a star schema (fact + dimension tables)

- **Data model:**
  - `audit_events` (fact) — one row per prompt event  
  - `users` (dimension)  
  - `departments` (dimension)  
  - `pii_events` (child table) — one row per detected PII instance  

- SQL query library across three categories:

  **Operational**
  - daily request volume  
  - cost per user / department  
  - blocked vs. cleared ratios  

  **Risk / Quality**
  - repeat PII offenders  
  - abnormal cost outliers  
  - PII rate trends over time  

  **Validation**
  - orphan record detection  
  - impossible state checks (e.g., blocked + tokens consumed)  
  - cost sanity checks  

- Techniques used:
  - window functions (`RANK`, `AVG OVER`, `LAG`)  
  - Common Table Expressions (CTEs)  
  - aggregations and filtering (`GROUP BY`, `HAVING`)  

- Data contract between ingestion and analytics layers documented in:
  `docs/field_mapping.md`

**Directory:** `tpa-query-layer/`

---

## Data Flow

1. A prompt enters the pipeline  
2. The system scans for PII using regex rules  
3. The request is classified as `BLOCKED` or `CLEARED`  
4. Cleared requests are sent to the Claude API  
5. All events are logged to the `request_logs` table  
6. The ETL process transforms raw logs into structured tables  
7. SQL queries generate insights on usage, cost, and risk  

---

## Example Use Cases

- Monitor how often sensitive data is sent to LLMs  
- Track token usage and estimated cost by user or department  
- Identify high-risk prompt patterns and repeat offenders  
- Analyze blocked vs. cleared request trends over time  
- Support governance, compliance, and audit reporting  

---

## Tech Stack

- **Python** → ingestion pipeline and ETL  
- **SQLite** → logging and analytical storage  
- **SQL** → analytics and validation queries  
- **Anthropic Claude API** → LLM integration  
- **Regex** → PII detection engine  
- **Data Modeling** → star schema (fact + dimension design)  
- **Advanced SQL** → window functions, CTEs, aggregations  

---

## Future Improvements

- Replace regex with ML-based PII detection  
- Add live prompt input (currently uses hardcoded mock requests)  
- Migrate from SQLite to PostgreSQL for production scale  
- Add dbt models for versioned transformations  
- Build rule-based monitoring for alerting on audit patterns  

---

## Author

Selesa Kaoga
