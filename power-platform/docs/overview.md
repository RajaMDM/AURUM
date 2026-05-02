# AURUM Power Platform Companion Track

Maps the five AURUM stages to Microsoft Power Platform components.

| AURUM Stage | Power Platform Layer |
|-------------|---------------------|
| ASSAY       | Power Automate — source system connectors, data ingestion flows |
| UNEARTH     | AI Builder — form processing, anomaly prediction models |
| REFINE      | Dataverse — entity relationships, duplicate detection, merge |
| UNFURL      | Power Apps (model-driven) — golden record viewer; Power Pages — external portal |
| MARK        | Dataverse audit log + Power Automate — reverse sync flows |

## Dataverse Schema Approach
Each domain is modelled as a Dataverse table with:
- Standard columns mapped to AURUM canonical fields
- Custom columns for domain-specific attributes
- Relationships to parent/child entities
- Status reason values matching AURUM lifecycle states

See `dataverse-schemas/` for YAML definitions deployable via PAC CLI.
