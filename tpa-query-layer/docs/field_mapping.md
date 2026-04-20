\# Field Mapping: Pipeline to Query Layer



Data contract between Layer 1 (TPA Governance Pipeline) and Layer 2 (TPA Query Layer).



\## Source: Layer 1 request\_logs



Columns: id, timestamp, user\_id, department, use\_case, original\_input, pii\_detected, pii\_count, action, input\_tokens, output\_tokens, total\_tokens, cost\_usd, ai\_response.



\## Target: Layer 2 star schema



\### audit\_events (fact)

\- event\_id = request\_logs.id

\- event\_timestamp = request\_logs.timestamp

\- user\_id = FK lookup in users dim

\- department\_id = FK lookup in departments dim

\- pii\_detected = 0 if pii\_count=0 else 1

\- routing\_decision = request\_logs.action (renamed)

\- prompt\_tokens = request\_logs.input\_tokens (renamed)

\- response\_tokens = request\_logs.output\_tokens (renamed)

\- cost\_usd = request\_logs.cost\_usd



\### users (dim)

\- user\_id = sequential ID assigned during ETL

\- username = request\_logs.user\_id (raw code like "A123")

\- department\_id = FK

\- role = defaulted to "Unknown" (not in source)



\### departments (dim)

\- department\_id = sequential ID

\- department\_name = DISTINCT values from request\_logs.department

\- cost\_center = generated as CC{1000+id}



\### pii\_events (child)

\- pii\_event\_id = auto-increment

\- event\_id = FK to audit\_events

\- pii\_type = split from comma-separated pii\_detected string

\- matched\_text = defaulted to \[REDACTED]



\## Key transformations



1\. Department text -> dimension table with FK

2\. User code -> dimension table with FK

3\. PII comma-string -> child rows (one per match)

4\. Field renames: action -> routing\_decision, input\_tokens -> prompt\_tokens, output\_tokens -> response\_tokens

5\. Dropped fields: use\_case, original\_input, ai\_response, pii\_count, total\_tokens



\## Idempotency



ETL drops and recreates target tables on every run. Production would use incremental loads with watermarks.

