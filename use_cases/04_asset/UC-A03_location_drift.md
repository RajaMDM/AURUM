# UC-A03: Location Drift

## Summary
A fleet of 30 POS terminals was physically moved from the Dubai Mall store to the new Marina Walk store during a fit-out. The FM team updated their system. The CMDB and ERP still show Dubai Mall. Now IT support tickets go to the wrong office, maintenance engineers are dispatched to the wrong location, and insurance coverage may be void because the insured location is wrong.

## Domain
Asset

## AURUM Stage(s)
REFINE · UNFURL · MARK

## Business Impact
- IT support engineers dispatched to Dubai Mall find nothing — wasted hours, SLA breach
- Maintenance contracts tied to location — wrong location means wrong contract applies
- Insurance: policy may require assets to be at the declared location
- Capex reporting: assets still appear under Dubai Mall cost centre, not Marina Walk

## Scenario Setup
30 POS terminals (AST-0301 to AST-0330) were relocated in October. FM system updated October 15. CMDB and ERP still show `LOC-001` (Dubai Mall). FM shows `LOC-012` (Marina Walk). AURUM detects the location conflict across sources.

## Example Records

| field | CMDB-0301 | ERP-0301 | FM-0301 |
|-------|-----------|---------|---------|
| asset_tag | AST-0301 | AST-0301 | AST-0301 |
| description | POS Terminal | POS Terminal | POS terminal |
| location_id | LOC-001 | LOC-001 | LOC-012 |
| lifecycle_state | Active | Active | Active |
| last_updated | 2024-08-10 | 2024-09-01 | 2024-10-15 |

## AURUM Pipeline Walk-Through

**ASSAY** — All three records ingest. Asset tag normalised. Location IDs mapped to canonical location golden record IDs.

**UNEARTH** — Asset profiler cross-record location conflict: same asset tag, different location across sources. FM has most recent `last_updated` → flagged as likely truth. Pattern: 30 consecutive asset tags all have the same FM→CMDB/ERP location discrepancy → batch relocation event detected.

**REFINE** — Clusters formed (30 separate clusters, one per asset). Survivorship for `location_id`: FM wins (most recent update). `LOCATION_CONFLICT` events logged for all 30.

**UNFURL** — 30 golden records updated with `location_id: LOC-012`. Reverse sync plan: push updated location to CMDB and ERP for all 30 assets.

**MARK** — `LOCATION_DRIFT(AST-0301..AST-0330: LOC-001 → LOC-012, source=FM, date=2024-10-15)` batch event logged.

## Stewardship Decision Point
Carlos (DataOps) reviews the batch event — 30 assets, same pattern, clearly a legitimate relocation. Approves bulk reverse sync. No individual steward review needed per asset. Cost centre realignment raised as a separate finance ticket.

## Expected Golden Record

| field | golden_value | source | confidence |
|-------|-------------|--------|------------|
| location_id | LOC-012 | FM (most recent) | 0.96 |
| location_name | Marina Walk Store | LOC master | 1.0 |
| lifecycle_state | Active | Consensus | 1.0 |

## CLI Demo Command
```bash
python -m runtimes.cli demo
```

## Related Use Cases
- [UC-A01](UC-A01_lifecycle_state_conflict.md) — Lifecycle state conflict (often accompanies location drift)
- [UC-L03](../05_location/UC-L03_store_warehouse_duplicate.md) — Duplicate location records that cause asset drift
