# UC-E02: Org Hierarchy Change — Reorg Impact on Master Data

## Summary
The company restructured its regional leadership in Q3. The "GCC Operations" division was split into "UAE Operations" and "KSA Operations". 47 employees who reported to the old division head now have dangling `manager_id` references (the manager record was retired) and incorrect department codes. AURUM detects the broken hierarchy and surfaces all impacted records for bulk reassignment.

## Domain
Employee

## AURUM Stage(s)
REFINE · UNFURL · MARK

## Business Impact
- Org chart tools show 47 employees with no manager — "orphaned" in the hierarchy
- Access provisioning broken: AD group memberships are manager-driven, so 47 employees may lose access to shared drives
- Performance review cycle cannot be initiated for employees with no active manager link
- Finance: cost centre rollup by manager broken — budget variance reports incomplete

## Scenario Setup
`EMP-00201` (Gaurav Mehta, VP GCC Operations) left the company. His record was set to `status: Inactive` in HRMS. 47 direct and indirect reports still reference `manager_id: EMP-00201`. The new structure splits his team into two new managers: `EMP-00445` (UAE) and `EMP-00512` (KSA).

## Example Records

| employee_id | name | manager_id | manager_status | dept |
|------------|------|-----------|---------------|------|
| EMP-00310 | Nadia Al-Hassan | EMP-00201 | Inactive | GCC Operations |
| EMP-00315 | Carlos Rivera | EMP-00201 | Inactive | GCC Operations |
| EMP-00320 | Jin Park | EMP-00201 | Inactive | GCC Operations |
| EMP-00201 | Gaurav Mehta | EMP-00100 | **Inactive** | GCC Operations |

## AURUM Pipeline Walk-Through

**ASSAY** — HRMS export ingested. `manager_id` referential integrity check: `EMP-00201` referenced by 47 records but has `status: Inactive` → `BROKEN_MANAGER_LINK` detected.

**UNEARTH** — Employee profiler org rules:
- `inactive_manager`: manager_id references an inactive employee → 47 records flagged HIGH
- `self_manager_check`: no employee is their own manager (clean)
- `orphan_depth`: employees with no valid manager path to root → 47 flagged

**REFINE** — The 47 affected employees can't be auto-reassigned (business decision). Grouped into a `REORG_BATCH` for bulk steward action. AURUM proposes splitting by location: UAE-based employees → `EMP-00445`, KSA-based → `EMP-00512`.

**UNFURL** — After steward approval, bulk update: 28 UAE employees get `manager_id: EMP-00445`, 19 KSA employees get `manager_id: EMP-00512`. Department updated from `GCC Operations` to `UAE Operations` / `KSA Operations`.

**MARK** — `REORG_EVENT(47 employees, GCC Operations dissolved, split to UAE/KSA, approved by Sofia PM, 2024-Q3)` logged. Full audit trail.

## Stewardship Decision Point
Amara (BA) and Sofia (PM) review the proposed split by location. Three employees are cross-border (based in UAE but report to KSA business) — manually assigned by HR Director. Remaining 44 auto-approved.

## Expected Golden Record
Each of 47 employees: updated `manager_id`, updated `department`, updated `cost_centre`. `reorg_event_id` stamped on each record for audit traceability.

## CLI Demo Command
```bash
python -m runtimes.cli unearth employee shared/sample_data/output/employees_dirty.csv
```

## Related Use Cases
- [UC-E05](UC-E05_cost_centre_realignment.md) — Cost centre realignment that follows a reorg
- [UC-L01](../05_location/UC-L01_hierarchy_conflict.md) — Location hierarchy mirrors employee org hierarchy
