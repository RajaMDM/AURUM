# Counterparty Domain — Use Cases

The **Counterparty domain** is the most complex MDM domain — counterparties can be customers, vendors, financial institutions, regulatory bodies, or all of the above simultaneously. The critical anchors are LEI (Legal Entity Identifier, ISO 17442) for financial counterparties and tax ID for commercial ones. Dual-role detection and jurisdiction consistency are the hardest problems.

## Use Cases

| Code | Title | Complexity | Key Stages |
|------|-------|-----------|------------|
| [UC-CP01](UC-CP01_dual_role_detection.md) | Dual-Role Detection — Vendor and Customer | High | REFINE, UNFURL, MARK |
| [UC-CP02](UC-CP02_lei_validation_failure.md) | LEI Validation Failure | Low | ASSAY, UNEARTH |
| [UC-CP03](UC-CP03_legal_entity_deduplication.md) | Legal Entity Deduplication | High | REFINE, UNFURL |
| [UC-CP04](UC-CP04_jurisdiction_mismatch.md) | Jurisdiction Mismatch | Medium | UNEARTH, REFINE |
| [UC-CP05](UC-CP05_relationship_lineage_audit.md) | Relationship Lineage Audit | High | MARK, UNFURL |
