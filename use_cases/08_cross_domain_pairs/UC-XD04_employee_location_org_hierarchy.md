# UC-XD04: Employee × Location — Org Hierarchy Mirrors Location Hierarchy

## Domains
Employee · Location

## Summary
The company's org structure and its physical location hierarchy should mirror each other: UAE North region employees work in UAE North locations, and their manager's manager maps to the regional director who owns those locations. After a reorg (UC-E02) updated the employee hierarchy, and a location hierarchy correction (UC-L05) updated the location tree, the two hierarchies are now out of sync with each other — employees in "UAE Operations" are assigned to locations still tagged under the old "GCC Operations" regional node.

## Business Impact
- Territory-based routing logic (route customer calls to the nearest team) breaks — location node doesn't match employee cost centre node
- Budget allocation: location costs roll up to one hierarchy, employee costs roll up to another — CFO can't get a unified view of the UAE Operations P&L
- Facilities planning: headcount per location is wrong — employees are allocated to one hierarchy, desks to another
- Emergency response: floor warden lists (employees by location) are wrong because the org ↔ location mapping is stale

## Scenario Setup

**Post-Reorg Employee State:**
- 28 employees now in `department: UAE Operations`, `cost_centre: CC-OPS-UAE`, `manager: EMP-00445`
- Their `location_id` still points to `LOC-R02` (UAE North) — the old location node that existed under the old "GCC Operations" hierarchy

**Post-Location-MDM State:**
- Location hierarchy corrected: `LOC-R02` renamed to `LOC-R02` (still exists) but is now a child of `GLD-LOC-R00 (UAE)` not `GLD-LOC-R-GCC (GCC)`
- 12 of the 28 employees' `location_id` points to `LOC-R02` correctly
- 16 employees have `location_id: LOC-R-GCC` (the old GCC node, now archived) → stale reference

## AURUM Pipeline Walk-Through

**Cross-Domain UNEARTH** — After both Employee and Location MDM runs:
- Referential integrity: 16 employee records reference `LOC-R-GCC` (archived) → `STALE_LOCATION_REF` flagged
- Hierarchy consistency: employee `cost_centre: CC-OPS-UAE` vs `location node: GCC` → `HIERARCHY_MISMATCH` flagged
- Pattern: all 16 are in the same department → batch event, same root cause

**Cross-Domain REFINE** — Auto-propose: employees with `department: UAE Operations` and `location_id: LOC-R-GCC` → update `location_id` to `LOC-R02` (UAE North, now under UAE hierarchy). Presented to steward for bulk approval.

**UNFURL** — After approval: 16 employee records updated with correct location_id. Facilities system receives updated employee-location assignments. Floor warden lists regenerated.

**MARK** — `CROSS_DOMAIN_SYNC(16 employees, location_id LOC-R-GCC → LOC-R02, trigger=reorg+location-hierarchy-correction)` logged.

## Stewardship Decision Point
Pierre (EA Head) and Sofia (PM) review jointly — this touches both the org design and the real estate portfolio. Confirm: all 16 employees physically sit in UAE North offices. Auto-approval granted. One employee (works remotely from KSA but is in UAE Ops org) manually flagged for an exception: `org_location: LOC-R02`, `physical_location: LOC-KSA-01`.

## Validated Cross-Domain View

```
Employee: Nadia
├── department: UAE Operations
├── manager_id: GLD-EMP-00445
├── cost_centre: CC-OPS-UAE
└── location_id: LOC-R02 (UAE North)
                    └── parent: GLD-LOC-R00 (UAE)
                                └── parent: GLD-LOC-R-WORLD
```

The org hierarchy and location hierarchy now tell the same story.

## CLI Demo Command
```bash
python -m runtimes.cli demo
```

## Related Use Cases
- [UC-E02](../06_employee/UC-E02_org_hierarchy_change.md) — The reorg that created the mismatch
- [UC-L05](../05_location/UC-L05_parent_child_resolution.md) — Location hierarchy correction
- [UC-GS01](../09_grand_scenario/UC-GS01_new_store_opening.md) — Grand scenario where org and location hierarchies are built together from day one
