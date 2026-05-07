# Location Domain — Use Cases

The **Location domain** mastering challenge is resolving hierarchy conflicts (which store reports to which region), detecting geocoding drift (lat/lon that no longer matches the address), and deduplicating near-identical location records created by different teams across ERP, WMS, YEXT, and CRM. Parent-child relationships are the critical hierarchy anchor.

## Use Cases

| Code | Title | Complexity | Key Stages |
|------|-------|-----------|------------|
| [UC-L01](UC-L01_hierarchy_conflict.md) | Hierarchy Conflict — Region vs Store Rollup | High | REFINE, UNFURL, MARK |
| [UC-L02](UC-L02_geocoding_drift.md) | Geocoding Drift — Null Island Detection | Low | UNEARTH |
| [UC-L03](UC-L03_store_warehouse_duplicate.md) | Store vs Warehouse Duplicate | Medium | REFINE, UNFURL |
| [UC-L04](UC-L04_address_standardisation.md) | Address Standardisation | Low | ASSAY, UNEARTH |
| [UC-L05](UC-L05_parent_child_resolution.md) | Parent-Child Location Resolution | High | REFINE, UNFURL, MARK |
