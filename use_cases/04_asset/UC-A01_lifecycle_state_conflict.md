# UC-A01: Lifecycle State Conflict

## Summary
A Dell laptop (asset tag AST-0112) is recorded as "Active" in the CMDB, "In Use" in ERP, and "Maintenance" in the FM system — three different lifecycle states for the same physical asset. No system is wrong per se; they use different vocabularies. But when the finance team runs a depreciation report, the asset appears three times with conflicting states, causing incorrect asset valuation and audit failures.

## Domain
Asset

## AURUM Stage(s)
UNEARTH · REFINE

## Business Impact
- Depreciation schedules computed against wrong lifecycle state (Maintenance assets depreciate differently)
- IT refresh planning wrong — "Active" assets are included in refresh cycle, "Maintenance" ones aren't
- Insurance policy: insured value may exclude assets flagged as "Retired" — if wrongly flagged, loss isn't covered
- ISO 55000 asset management compliance requires accurate lifecycle state

## Scenario Setup
The laptop was sent to the IT repair team 2 weeks ago. FM updated its record to "Maintenance". CMDB still shows "Active" (not updated by the helpdesk). ERP shows "In Use" (the original state from provisioning — never updated).

## Example Records

| field | CMDB-00112 | ERP-00112 | FM-00112 |
|-------|------------|-----------|----------|
| asset_tag | AST-0112 | AST-0112 | ast-0112 |
| serial_number | SN-DELL-4521X | SN-DELL-4521X | |
| lifecycle_state | Active | In Use | Maintenance |
| description | Dell Laptop | Dell Laptop | HP Laptop |
| last_updated | 2024-09-01 | 2024-03-15 | 2024-11-18 |

## AURUM Pipeline Walk-Through

**ASSAY** — Three records ingest. Asset tag normalised (strip, uppercase, hyphen-standardise) → all map to `AST-0112`.

**UNEARTH** — Asset profiler lifecycle whitelist: `In Use` not in approved whitelist `[Active, Maintenance, Retired, Disposed]` → flagged. Cross-record state conflict detected: 3 states for same asset tag. Description conflict: `HP Laptop` vs `Dell Laptop` → HIGH anomaly (different manufacturer).

**REFINE** — Cluster formed (asset tag + serial number exact match). Survivorship: most recent `last_updated` wins for lifecycle_state → FM wins with `Maintenance`. Description conflict flagged for steward: "Dell Laptop" (2 sources) vs "HP Laptop" (FM) — likely data entry error in FM.

## Stewardship Decision Point
Steward confirms: it IS a Dell laptop, FM record has a description typo. `Maintenance` state is correct (sent for repair). CMDB and ERP updated via reverse sync.

## Expected Golden Record

| field | golden_value | source | confidence |
|-------|-------------|--------|------------|
| asset_tag | AST-0112 | Consensus | 1.0 |
| lifecycle_state | Maintenance | FM (most recent) | 0.93 |
| description | Dell Laptop | CMDB/ERP consensus | 0.98 |
| serial_number | SN-DELL-4521X | CMDB/ERP | 1.0 |

## CLI Demo Command
```bash
python -m runtimes.cli unearth asset shared/sample_data/output/assets_dirty.csv
```

## Related Use Cases
- [UC-A03](UC-A03_location_drift.md) — Location drift often co-occurs with lifecycle state conflicts
