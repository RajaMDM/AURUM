# UC-V02: Group/Subsidiary Hierarchy Conflict

## Summary
Carrefour UAE (a subsidiary) and Majid Al Futtaim Group (the parent holding company) are both registered as separate vendors in the ERP. Contracts are with the subsidiary, but payment guarantees are with the group. Without hierarchy resolution, spend analytics show two vendors when they should show one group with a subsidiary child — causing incorrect strategic sourcing decisions and missed volume discount thresholds.

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
ERP has `Carrefour UAE LLC` and `Majid Al Futtaim Retail LLC` as separate vendors. Procurement knows these are parent/subsidiary but never set the relationship in the system. AP is paying both. PROCUREMENT portal has the group entity `Majid Al Futtaim Group` as the contract counterparty.

## Example Records

| field | ERP-V101 | ERP-V102 | PROC-V200 |
|-------|----------|----------|-----------|
| legal_name | Carrefour UAE LLC | Majid Al Futtaim Retail LLC | Majid Al Futtaim Group |
| trading_name | Carrefour | MAF Retail | MAF Group |
| tax_id | TRN100345001 | TRN100345002 | TRN100345000 |
| parent_vendor_id | | | |
| country | UAE | UAE | UAE |

## AURUM Pipeline Walk-Through

**ASSAY** — Three records ingest. TRN prefix analysis: `TRN100345001`, `TRN100345002`, `TRN100345000` — same prefix `TRN10034500x` suggests same TRN root → likely same corporate group.

**UNEARTH** — Vendor profiler: self-parent check (no vendor is its own parent). Flags: `parent_vendor_id` is null on all three — hierarchy not set. Name similarity: `Majid Al Futtaim Retail` vs `Majid Al Futtaim Group` = 0.89. Flagged for hierarchy review.

**REFINE** — Cluster NOT formed (these are genuinely separate legal entities). Instead: HIERARCHY_LINK proposed: `ERP-V101 → parent: ERP-V102`, `ERP-V102 → parent: PROC-V200`. Presented to steward for confirmation.

**UNFURL** — Three golden records published with parent_id links set. Spend analytics can now roll up from Carrefour UAE → MAF Retail → MAF Group.

**MARK** — `HIERARCHY_ESTABLISHED(Carrefour UAE → MAF Retail → MAF Group)` logged.

## Stewardship Decision Point
Steward must confirm the parent-child relationships — AURUM proposes based on TRN prefix and name similarity but cannot auto-assert corporate hierarchy without human confirmation. This is a HIGH-stakes decision with legal and financial implications.

## Expected Golden Record
Three separate golden records with hierarchy:
- `GLD-VEND-0200` (MAF Group) — root parent
- `GLD-VEND-0102` (MAF Retail) — `parent_id: GLD-VEND-0200`
- `GLD-VEND-0101` (Carrefour UAE) — `parent_id: GLD-VEND-0102`

## CLI Demo Command
```bash
python -m runtimes.cli unearth vendor shared/sample_data/output/vendors_dirty.csv
```

## Related Use Cases
- [UC-V01](UC-V01_legal_vs_trading_entity.md) — Legal vs trading entity for a single vendor
- [UC-CP03](../07_counterparty/UC-CP03_legal_entity_deduplication.md) — Legal entity dedup for counterparties
