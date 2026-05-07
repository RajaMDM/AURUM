# Customer Domain — Use Cases

The **Customer domain** is the most commonly mastered domain in enterprise MDM. The core challenge is identity resolution: a single real-world customer may exist across CRM, e-commerce, ERP, and loyalty systems with name variants, format differences, and conflicting attribute values. AURUM's REFINE stage handles this with composite fuzzy matching, transitive clustering, and trust-weighted survivorship.

## Use Cases

| Code | Title | Complexity | Key Stages |
|------|-------|-----------|------------|
| [UC-C01](UC-C01_identity_resolution.md) | Identity Resolution Across Source Systems | Medium | ASSAY, UNEARTH, REFINE, UNFURL, MARK |
| [UC-C02](UC-C02_cross_channel_merge.md) | Cross-Channel Merge with Conflicting Loyalty Tiers | Medium | UNEARTH, REFINE, UNFURL, MARK |
| [UC-C03](UC-C03_dq_email_phone_failure.md) | DQ Failure — Missing Email and Invalid Phone | Low | ASSAY, UNEARTH |
| [UC-C04](UC-C04_golden_record_conflict.md) | Golden Record Conflict — Address Field Disagreement | High | REFINE, UNFURL, MARK |
| [UC-C05](UC-C05_lineage_audit_trail.md) | Customer Lineage Audit Trail | Medium | MARK, UNFURL |
