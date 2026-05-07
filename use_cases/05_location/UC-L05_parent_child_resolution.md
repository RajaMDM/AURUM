# UC-L05: Parent-Child Location Resolution

## Summary
The UAE location hierarchy should be: Country → Emirate → City → District → Store/Warehouse. In practice, 40% of location records have a missing or incorrect parent_id — some stores reference an Emirate as their parent (skipping City), some warehouses reference a Store as their parent (wrong hierarchy level), and some have no parent at all. AURUM reconstructs the correct hierarchy using city/emirate inference rules and steward confirmation.

## Domain
Location

## AURUM Stage(s)
REFINE · UNFURL · MARK

## Business Impact
- Hierarchy-based reporting collapses: Emirate-level P&L rollup breaks when stores reference the wrong parent
- Territory assignment fails: sales territory rules are parent-based — wrong parent = wrong territory
- Org design: if locations drive cost centre hierarchies, wrong parent means wrong cost centre tree
- Real estate: portfolio view by Emirate is wrong — some stores missing from their Emirate rollup

## Scenario Setup
30 location records have parent hierarchy issues. The correct UAE hierarchy is: `UAE (LOC-R00)` → `Dubai (LOC-R01)` → `Downtown Dubai (LOC-R03)` → `Dubai Mall Store (LOC-001)`. But the WMS has `Dubai Mall Store` → parent: `UAE` (skipping two levels). The CRM has `Marina Walk Store` → parent: `Dubai Mall Store` (wrong — sibling, not parent).

## Example Records

| location_code | name | parent_id | parent_name | issue |
|--------------|------|-----------|-------------|-------|
| LOC-001 | Dubai Mall Store | LOC-R00 | UAE | Skips Emirate+City levels |
| LOC-009 | Marina Walk Store | LOC-001 | Dubai Mall Store | Sibling treated as parent |
| LOC-015 | Abu Dhabi HQ | | | No parent at all |
| LOC-020 | Sharjah Warehouse | LOC-R01 | Dubai | Wrong Emirate (Sharjah ≠ Dubai) |

## AURUM Pipeline Walk-Through

**ASSAY** — All location records ingest. Parent_id referential integrity check: all parent_ids resolve to existing location records (no broken references, but some are logically wrong).

**UNEARTH** — Location profiler hierarchy rules:
- `hierarchy_level_skip`: if location type=Store and parent type=Country (skipping 2 levels) → flagged
- `sibling_as_parent`: if location type=Store and parent type=Store → flagged (Store can't be parent of Store in this model)
- `emirate_city_mismatch`: if city=Sharjah and parent resolves to Dubai Emirate → flagged

**REFINE** — AURUM infers correct parents using city/emirate fields:
- `LOC-001` city=Dubai → correct parent chain: UAE→Dubai→Downtown Dubai (auto-proposed)
- `LOC-009` city=Dubai → correct parent: Dubai district (auto-proposed, NOT Dubai Mall)
- `LOC-015` city=Abu Dhabi → parent chain: UAE→Abu Dhabi (auto-proposed)
- `LOC-020` city=Sharjah → parent: UAE→Sharjah (auto-proposed, not Dubai)
All proposals sent to steward for confirmation before publishing.

**UNFURL** — After steward sign-off, hierarchy corrected for all 30 records. Full location tree now consistent.

**MARK** — `HIERARCHY_CORRECTED(LOC-001: LOC-R00 → LOC-R03)`, `HIERARCHY_CORRECTED(LOC-009: LOC-001 → LOC-R03)` etc. logged for audit.

## Stewardship Decision Point
Pierre (EA Head) reviews and approves the proposed hierarchy corrections. One record (LOC-015 Abu Dhabi HQ) needs a new intermediate node `Abu Dhabi City Centre (LOC-R06)` — Pierre creates it in the location master before approving the link.

## Expected Golden Record
`LOC-001 (Dubai Mall Store)`: `parent_id: LOC-R03 (Downtown Dubai)`, hierarchy depth = 4.
`LOC-009 (Marina Walk Store)`: `parent_id: LOC-R03 (Downtown Dubai)`, sibling of LOC-001.

## CLI Demo Command
```bash
python -m runtimes.cli unearth location shared/sample_data/output/locations_dirty.csv
```

## Related Use Cases
- [UC-L01](UC-L01_hierarchy_conflict.md) — Hierarchy conflict when parent_id differs across sources
- [UC-XD04](../08_cross_domain_pairs/UC-XD04_employee_location_org_hierarchy.md) — Employee org hierarchy mirrors location hierarchy
