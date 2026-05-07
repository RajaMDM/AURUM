# UC-A02: Orphaned Asset Detection

## Summary
142 assets in the CMDB have no `location_id` and no `assigned_to` field — they exist in the system with no physical anchor. These orphaned assets can't be verified in a physical audit, can't be included in insurance valuations, and represent potential ghost assets (assets that were disposed of or stolen but never written off). AURUM's UNEARTH stage systematically flags all orphans for steward action.

## Domain
Asset

## AURUM Stage(s)
UNEARTH

## Business Impact
- Ghost assets inflate the fixed asset register — overstated balance sheet
- Insurance premiums paid on assets that don't exist
- Physical audit failures — auditors flag unverifiable assets
- Stolen assets not reported to police/insurance because no one knows they're missing
- IFRS 16 / IAS 16: assets must be identifiable and controlled — orphans fail this test

## Scenario Setup
A legacy CMDB migration brought over 5 years of asset records. Many were disposed, transferred, or lost without being updated in the system. The migration script didn't validate `location_id` referential integrity — it imported whatever was there, including nulls.

## Example Records

| asset_tag | description | lifecycle_state | location_id | assigned_to |
|-----------|------------|----------------|------------|-------------|
| AST-0201 | POS Terminal | Active | | |
| AST-0202 | HVAC Unit | In Use | | maintenance_team |
| AST-0203 | Laptop | Retired | | |
| AST-0204 | Server Rack | Active | LOC-005 | it_infra |
| AST-0205 | iPad | Active | | |

## AURUM Pipeline Walk-Through

**ASSAY** — Schema inspector: `location_id` null rate = 28% (threshold: 5%). Flagged as HIGH severity null rate anomaly.

**UNEARTH** — Asset profiler orphan detection rules:
- `orphan_no_location`: `location_id` null AND `assigned_to` null → 142 records flagged as FULL_ORPHAN
- `orphan_partial`: `location_id` null but `assigned_to` present → 38 records flagged as PARTIAL_ORPHAN (can trace via person)
- `orphan_retired_ok`: `lifecycle_state = Retired` AND `location_id` null → acceptable (15 records, demoted to LOW severity)
- Anomaly detector: cluster of assets with matching description and no location → possible batch disposal event

**REFINE** — Orphaned assets form singleton clusters (can't match without location/owner anchor). Published with `verification_required: true`.

## Stewardship Decision Point
Jin (Data Stewardship Lead) runs a physical audit sweep using the orphan report. For each orphan: physically locate it → update location_id, OR confirm it no longer exists → update lifecycle_state to `Disposed` and record disposal date. Target: reduce orphan count from 142 to < 10.

## Expected Golden Record
After remediation: `location_id: LOC-023`, `assigned_to: it_infra`, `lifecycle_state: Active`, `verified_date: 2024-11-25`.
Confirmed ghost assets: `lifecycle_state: Disposed`, `disposal_date: 2024-11-25`, `disposal_reason: PHYSICAL_AUDIT_NOT_FOUND`.

## CLI Demo Command
```bash
python -m runtimes.cli unearth asset shared/sample_data/output/assets_dirty.csv
```

## Related Use Cases
- [UC-A03](UC-A03_location_drift.md) — Location drift (assets that move without being updated)
- [UC-XD02](../08_cross_domain/UC-XD02_asset_location_employee_triangle.md) — Asset-Location-Employee cross-domain triangle
