# Vendor Domain — Use Cases

The **Vendor domain** mastering challenge is distinguishing legal entities from trading entities, resolving group vs. subsidiary hierarchies, and detecting duplicate vendor records that result in split payment runs, duplicate purchase orders, and compliance gaps. Tax ID validation and legal name standardisation are the critical DQ anchors.

## Use Cases

| Code | Title | Complexity | Key Stages |
|------|-------|-----------|------------|
| [UC-V01](UC-V01_legal_vs_trading_entity.md) | Legal vs Trading Entity Resolution | High | ASSAY, REFINE, UNFURL |
| [UC-V02](UC-V02_group_subsidiary_hierarchy.md) | Group/Subsidiary Hierarchy Conflict | High | REFINE, UNFURL, MARK |
| [UC-V03](UC-V03_tax_id_dq_failure.md) | Tax ID DQ Failure | Low | ASSAY, UNEARTH |
| [UC-V04](UC-V04_duplicate_vendor_detection.md) | Duplicate Vendor Detection | Medium | REFINE, UNFURL |
| [UC-V05](UC-V05_vendor_customer_crossover.md) | Vendor-Customer Crossover (Dual Role) | High | REFINE, UNFURL, MARK |
