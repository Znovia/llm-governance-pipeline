# TPA Governance Pipeline

Python pipeline that scans LLM prompts for PII, routes them through binary BLOCKED / CLEARED logic, and logs every transaction to SQLite. Part of a three-layer AI governance project: pipeline -> query layer -> monitor (in progress).

Related: https://github.com/Znovia/tpa-query-layer

## What this does

- Intercepts prompts before they hit the Claude API
- Scans for PII (SSN, account numbers, phone, email, credit card, routing numbers) using regex
- Routes every prompt: BLOCKED (PII found) or CLEARED
- Logs prompt, detection result, routing decision, response, and token counts to SQLite
- Tracks token-level cost per request

## Stack

Python, SQLite, Regex, Anthropic Claude API

## Data model

Every request is written to a single request_logs table with columns for timestamp, user_id, department, use_case, original_input, pii_detected (comma-separated types), pii_count, action (BLOCKED or CLEARED), input_tokens, output_tokens, total_tokens, cost_usd, and ai_response.

This raw log table is the input to Layer 2, where it gets normalized into a star schema with separate fact and dimension tables for analysis.

## How to run

Create a local .env file with your API key, install anthropic and python-dotenv via pip, then run: python tpa_pipeline_final.py

## Limitations

- Regex-based detection, not ML
- Single-user, local execution
- SQLite for portfolio simplicity
- Mock requests hardcoded in the script

## Next steps

- Migrate logs to Postgres
- Add retry and queue logic for API failures
- Feed logs into Layer 2 (Query Layer) for analytics
- Build Layer 3 (Monitor) for rule-based alerting