# UC-E05: Cost Centre Realignment

## Summary
Following a Q3 reorg, 23 employees moved from the old `CC-OPS-GCC` cost centre to new ones (`CC-OPS-UAE` or `CC-OPS-KSA`). Payroll was updated. HRMS was updated. But ERP still shows the old cost centre on all 23 records — causing monthly management accounts to show AED 2.1M of salary costs in a cost centre that no longer exists, and zero in the two new ones.

## Domain
Employee

## AURUM Stage(s)
REFINE · UNFURL · MARK

## Business Impact
- Management accounts wrong — CFO's monthly P&L has AED 2.1M in wrong cost centres
- Budget variance reporting broken — budgets are set on new cost centres, actuals posting to old
- Payroll reconciliation: HRMS cost centre ≠ ERP cost centre → automated reconciliation fails
- Headcount reporting: FTE counts wrong by cost centre for all three affected cost centres

## Scenario Setup
HRMS was updated first (correctly). Payroll was updated (batch job). ERP was supposed to be updated by a scheduled interface job, but the job failed silently — no error raised, no records updated. The mismatch wasn't detected until month-end close, 3 weeks later.

## Example Records

| employee_id | name | HRMS cost_centre | ERP cost_centre | Payroll cost_centre |
|------------|------|-----------------|----------------|-------------------|
| EMP-00310 | Nadia | CC-OPS-UAE | CC-OPS-GCC | CC-OPS-UAE |
| EMP-00315 | Carlos | CC-OPS-KSA | CC-OPS-GCC | CC-OPS-KSA |
| EMP-00320 | Jin | CC-OPS-UAE | CC-OPS-GCC | CC-OPS-UAE |

## AURUM Pipeline Walk-Through

**ASSAY** — HRMS, ERP, and Payroll records ingested. Cost centre field has conflicting values across sources for the same employees.

**UNEARTH** — Employee profiler: cross-record cost centre conflict detected for 23 employees. `CC-OPS-GCC` appears in ERP but not in HRMS or Payroll for the same employees → `COST_CENTRE_MISMATCH` flagged. Pattern: same 23 employees all show same pattern → batch interface failure suspected.

**REFINE** — Clusters formed. Survivorship: HRMS is system of record for cost centre (most recently updated, HR-owned). ERP conflict flagged. Correct cost centre resolved from HRMS.

**UNFURL** — Golden records published with correct cost centres. Reverse sync plan to ERP generated for all 23 records.

**MARK** — `COST_CENTRE_CONFLICT(23 employees, ERP=CC-OPS-GCC stale, HRMS/Payroll=correct, root_cause=interface_failure)` logged. Carlos (DataOps) notified to investigate and fix the ERP interface job.

## Stewardship Decision Point
Finance Controller confirms the correct cost centres from the org chart effective dates. Approves bulk ERP reverse sync. Root cause investigation (interface failure) raised as a separate IT ticket by Carlos.

## Expected Golden Record
All 23 employees: `cost_centre: CC-OPS-UAE or CC-OPS-KSA` (per HRMS), `cost_centre_effective_date: 2024-07-01`, ERP updated via reverse sync.

## CLI Demo Command
```bash
python -m runtimes.cli demo
```

## Related Use Cases
- [UC-E02](UC-E02_org_hierarchy_change.md) — The reorg that triggered this cost centre change
- [UC-XD04](../08_cross_domain_pairs/UC-XD04_employee_location_org_hierarchy.md) — Location-based cost centre assignment
