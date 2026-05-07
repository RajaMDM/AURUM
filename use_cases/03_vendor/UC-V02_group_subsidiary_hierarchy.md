# UC-V02: Group/Subsidiary Hierarchy Conflict

## Summary
FreshMart UAE (a subsidiary) and Apex Retail Group (the parent holding company) are both registered as separate vendors in the ERP. Contracts are with the subsidiary, but payment guarantees are with the group. Without hierarchy resolution, spend analytics show two vendors when they should show one group with a subsidiary child — causing incorrect strategic sourcing decisions and missed volume discount thresholds.

## Domain
Vendor

## AURUM Stage(s)
REFINE · UNFURL · MARK

## Business Impact
- Volume discount thresholds missed because spend is split across parent and subsidiary records
- Sourcing analytics show wrong "number of vendors" KPI — inflated by unresolved hierarchies
- Credit limit management fails — credit is checked against subsidiary only, not group guarantee
- ESG reporting: supplier diversity metrics miscounted

## Scenario Setup
ERP has `FreshMart UAE LLC` and `Apex Retail LLC` as separate vendors. Procurement knows these are parent/subsidiary but never set the relationship in the system. AP is paying both. PROCUREMENT portal has the group entity `Apex Retail Group` as the contract counterparty.

## Example Records

| field | ERP-V101 | ERP-V102 | PROC-V200 |
|-------|----------|----------|-----------|
| legal_name | FreshMart UAE LLC | Apex Retail LLC | Apex Retail Group |
| trading_name | FreshMart | Apex Retail | Apex Group |
| tax_id | TRN100345001 | TRN100345002 | TRN100345000 |
| parent_vendor_id | | | |
| country | UAE | UAE | UAE |

## AURUM Pipeline Walk-Through

**ASSAY** — Three records ingest. TRN prefix analysis: `TRN100345001`, `TRN100345002`, `TRN100345000` — same prefix `TRN10034500x` suggests same TRN root → likely same corporate group.

**UNEARTH** — Vendor profiler: self-parent check (no vendor is its own parent). Flags: `parent_vendor_id` is null on all three — hierarchy not set. Name similarity: `Apex Retail` vs `Apex Retail Group` = 0.89. Flagged for hierarchy review.

**REFINE** — Cluster NOT formed (these are genuinely separate legal entities). Instead: HIERARCHY_LINK proposed: `ERP-V101 → parent: ERP-V102`, `ERP-V102 → parent: PROC-V200`. Presented to steward for confirmation.

**UNFURL** — Three golden records published with parent_id links set. Spend analytics can now roll up from FreshMart UAE → Apex Retail → Apex Group.

**MARK** — `HIERARCHY_ESTABLISHED(FreshMart UAE → Apex Retail → Apex Group)` logged.

## Stewardship Decision Point
Steward must confirm the parent-child relationships — AURUM proposes based on TRN prefix and name similarity but cannot auto-assert corporate hierarchy without human confirmation. This is a HIGH-stakes decision with legal and financial implications.

## Expected Golden Record
Three separate golden records with hierarchy:
- `GLD-VEND-0200` (Apex Group) — root parent
- `GLD-VEND-0102` (Apex Retail) — `parent_id: GLD-VEND-0200`
- `GLD-VEND-0101` (FreshMart UAE) — `parent_id: GLD-VEND-0102`

## CLI Demo Command
```bash
python -m runtimes.cli unearth vendor shared/sample_data/output/vendors_dirty.csv
```

## Related Use Cases
- [UC-V01](UC-V01_legal_vs_trading_entity.md) — Legal vs trading entity for a single vendor
- [UC-CP03](../07_counterparty/UC-CP03_legal_entity_deduplication.md) — Legal entity dedup for counterparties
