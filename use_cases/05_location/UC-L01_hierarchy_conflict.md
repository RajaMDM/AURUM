# UC-L01: Hierarchy Conflict — Region vs Store Rollup

## Summary
The Dubai Mall store reports to "UAE North" region in ERP but to "GCC Retail" region in the YEXT directory system. The CRM has it under "UAE" with no sub-region at all. When the regional VP runs a revenue report by region, the Dubai Mall store's numbers appear in three different rollup buckets depending on which system she uses. AURUM resolves the hierarchy conflict and establishes a single authoritative location tree.

## Domain
Location

## AURUM Stage(s)
REFINE · UNFURL · MARK

## Business Impact
- Regional P&L reports are wrong — Dubai Mall revenue double-counted or missed depending on report source
- Territory management broken — sales reps don't know which regional manager owns Dubai Mall
- Incentive calculations wrong — regional managers' bonuses tied to wrong store set
- Real estate portfolio reporting: IFRS 16 lease obligations must roll up correctly

## Scenario Setup
Dubai Mall Store (LOC-001) has three parent_id values across systems: ERP says `LOC-R02` (UAE North), YEXT says `LOC-R05` (GCC Retail), CRM says `LOC-C01` (UAE). All three parent records are themselves valid locations. The conflict is a true hierarchy disagreement — different teams set it up differently.

## Example Records

| field | ERP LOC-001 | YEXT LOC-001 | CRM LOC-001 |
|-------|-------------|--------------|-------------|
| location_code | LOC-001 | LOC-001 | LOC-001 |
| name | Dubai Mall Store | Dubai Mall | Dubai Mall Store |
| parent_id | LOC-R02 (UAE North) | LOC-R05 (GCC Retail) | LOC-C01 (UAE) |
| type | Store | Store | Retail |
| last_updated | 2024-01-10 | 2024-07-22 | 2023-09-05 |

## AURUM Pipeline Walk-Through

**ASSAY** — Three records ingest, all map to LOC-001. Parent IDs reference different hierarchy trees.

**UNEARTH** — Location profiler self-parent check: none is its own parent (ok). Cross-record parent conflict: LOC-001 has 3 different parent_ids → `HIERARCHY_CONFLICT` flagged, HIGH severity.

**REFINE** — Cluster formed (location_code exact match). Survivorship: parent_id is a HIERARCHY field — cannot resolve by recency or source trust alone. Escalated to steward with all three competing hierarchies shown side by side.

**UNFURL** — Held in `PENDING_REVIEW` until steward resolves. Other location fields (name, type, city) resolved and published. `parent_id` field left blank with `conflict_flag: HIERARCHY_CONFLICT`.

**MARK** — `HIERARCHY_CONFLICT(LOC-001: ERP=LOC-R02, YEXT=LOC-R05, CRM=LOC-C01)` logged for audit.

## Stewardship Decision Point
Sofia (PM) and Pierre (EA Head) jointly define the authoritative location hierarchy — this is a business decision, not a data decision. They establish: the ERP hierarchy (UAE North / UAE South / GCC) is the financial reporting hierarchy. YEXT is the marketing directory hierarchy — both are valid, but for MDM purposes the ERP hierarchy is canonical.

## Expected Golden Record

| field | golden_value | source | confidence |
|-------|-------------|--------|------------|
| parent_id | LOC-R02 | ERP (authoritative financial hierarchy) | 1.0 |
| name | Dubai Mall Store | ERP/CRM consensus | 0.97 |
| type | Store | ERP/CRM consensus | 0.98 |

## CLI Demo Command
```bash
python -m runtimes.cli unearth location shared/sample_data/output/locations_dirty.csv
```

## Related Use Cases
- [UC-L05](UC-L05_parent_child_resolution.md) — Full parent-child tree resolution
- [UC-XD04](../08_cross_domain_pairs/UC-XD04_employee_location_org_hierarchy.md) — Employee org hierarchy tied to location hierarchy
