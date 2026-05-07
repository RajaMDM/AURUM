# Asset Domain — Use Cases

The **Asset domain** mastering challenge centres on lifecycle state inconsistency, orphaned assets (no location or owner), and the accumulation of near-duplicate records from CMDB, ERP, FM, and ITSM systems that each track assets independently. Serial number and asset tag normalisation are the primary match anchors.

## Use Cases

| Code | Title | Complexity | Key Stages |
|------|-------|-----------|------------|
| [UC-A01](UC-A01_lifecycle_state_conflict.md) | Lifecycle State Conflict | Low | UNEARTH, REFINE |
| [UC-A02](UC-A02_orphaned_asset_detection.md) | Orphaned Asset Detection | Low | UNEARTH |
| [UC-A03](UC-A03_location_drift.md) | Location Drift | Medium | REFINE, UNFURL, MARK |
| [UC-A04](UC-A04_serial_number_deduplication.md) | Serial Number Deduplication | Medium | ASSAY, REFINE |
| [UC-A05](UC-A05_maintenance_lineage_break.md) | Maintenance Lineage Break | High | MARK, UNFURL |
