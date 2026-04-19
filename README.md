# TPA Governance Pipeline

Python pipeline that scans LLM prompts for PII, routes them through binary BLOCKED/CLEARED logic, and logs every transaction to SQLite. Part of a three-layer AI governance project: pipeline → [query layer](https://github.com/Znovia/tpa-query-layer) → monitor (in progress).

## What this does

- Intercepts prompts before they hit the Claude API
- Scans for PII (SSN, account numbers, phone, email) using regex
- Routes every prompt: BLOCKED (PII found) or CLEARED
- Logs prompt, detection result, routing decision, response, and token counts to SQLite
- Tracks token-level cost per request

## Stack

Python, SQLite, Regex, Anthropic Claude API

## How to run

1. Set your API key in a local .env file:
2. Install dependencies:
3. Run the pipeline:
## Schema

Logs are stored in `request_logs` with fields for timestamp, user/department, PII detection, routing action, token counts, cost, and AI response.

## Limitations / next steps

- Regex-based detection (not ML)
- Single-user, local execution
- Next: migrate logs to Postgres, add retry/queue logic
