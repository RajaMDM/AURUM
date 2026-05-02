# ASSAY — Stage 01

**Metallurgical meaning:** Before a goldsmith processes raw ore, an assayer tests it — determines its composition, purity, and what's actually there before committing to the furnace. No assumptions. Just measurement.

**MDM meaning:** Before you touch source data, you inspect it. What fields exist? What formats? What's null? What's the cardinality? ASSAY gives you the facts so UNEARTH and REFINE start with full knowledge.

## Responsibilities
- Source connectivity and extraction
- Schema inspection and field profiling
- Format detection (email, phone, date, numeric, text)
- Migration assessment (CHARON pattern: assess → map → validate → cutover)

## Key Components
- `schema_inspector/` — field-level profiling of incoming datasets
- `connectors/` — source system adapters (CSV, REST, DB, flat file)
- `migration/` — CHARON migration cookbook

## When ASSAY is Complete
- Every source field is typed and null-profiled
- High-risk fields (high null, low cardinality, format anomalies) are flagged
- Schema map to AURUM canonical model is drafted
