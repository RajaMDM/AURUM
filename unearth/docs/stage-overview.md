# UNEARTH — Stage 02

**Metallurgical meaning:** Gold ore is buried in rock. Unearthing it means digging carefully to surface what's actually there — without destroying it. You don't process yet. You expose.

**MDM meaning:** UNEARTH surfaces what is hidden in your data — duplicates that haven't been caught, quality failures that have been ignored, anomalies no one knew existed. The profiler doesn't fix anything. It tells the truth.

## Responsibilities
- Domain-specific data quality rule execution
- Statistical profiling (completeness, consistency, format, uniqueness)
- ML-based anomaly detection (outliers, lifecycle mismatches, sudden value shifts)
- LLM-assisted rule generation from business descriptions

## Key Components
- `profiler/` — domain profilers for all 7 domains
- `dq_engine/` — rule execution engine
- `anomaly/` — ML anomaly detector
- `llm_rules/` — natural language → DQ rule compiler

## When UNEARTH is Complete
- Quality score per domain established
- All rule violations catalogued with row-level detail
- Anomalies flagged for steward review
- DQ baseline documented for post-golden comparison
