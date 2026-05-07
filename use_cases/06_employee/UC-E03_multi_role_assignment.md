# UC-E03: Multi-Role Assignment

## Summary
Shazia Hussain is the Data Quality Lead AND sits on the company's Data Governance Council as a named member. In HRMS she has one role. In the ERP project system she has a second role (`DGC Member`) with a different cost centre. In the AD she belongs to both the `DQ-Team` and `DGC-Members` groups. Three systems, three partial pictures of the same person's roles. AURUM links all role assignments to the single golden employee record.

## Domain
Employee

## AURUM Stage(s)
REFINE · UNFURL

## Business Impact
- Access reviews miss the DGC role (not in HRMS) — compliance gap
- Time and cost reporting split across two project codes for the same person — budgeting distorted
- When Shazia leaves, only the HRMS role is offboarded — DGC access and ERP project assignment remain active (security risk)
- Org design: headcount count inflated if multi-role employees are counted once per role record

## Scenario Setup
Shazia has a primary HRMS record (`EMP-00101`) and a secondary ERP project record (`PROJ-DGC-015`) that was created when she joined the governance council — treated as a separate "resource" in the project system, not linked to her employee record.

## Example Records

| field | HRMS EMP-00101 | ERP PROJ-DGC-015 | AD |
|-------|---------------|-------------------|-----|
| name | Shazia Hussain | S. Hussain | shussain |
| email | shazia.hussain@company.com | s.hussain@company.com | shazia.hussain@company.com |
| role | Data Quality Lead | DGC Member | — |
| department | Data Management | Governance | — |
| cost_centre | CC-DM-001 | CC-GOV-005 | — |

## AURUM Pipeline Walk-Through

**ASSAY** — HRMS, ERP, and AD records ingested to canonical employee schema. Email variants: `shazia.hussain` (HRMS/AD) vs `s.hussain` (ERP) — same domain.

**UNEARTH** — Employee profiler: email domain match across all three. Name: `Shazia Hussain` vs `S. Hussain` — 0.83 similarity. AD `shussain` maps to `shazia.hussain` via username convention check.

**REFINE** — Single cluster formed (email domain + name). NOT merged into one flat record — multi-role model applied: golden employee `GLD-EMP-00101` with `roles: [{primary: DQ Lead, cc: CC-DM-001}, {secondary: DGC Member, cc: CC-GOV-005}]`.

**UNFURL** — Golden record published with full role array. Identity governance system receives both roles for access review. Payroll gets primary role only (for compensation). Finance gets both cost centres with FTE split (0.8 / 0.2).

## Stewardship Decision Point
Shazia's line manager confirms the FTE split: 80% DQ Lead, 20% DGC. This is recorded as the time allocation in the golden record.

## Expected Golden Record

| field | golden_value |
|-------|-------------|
| employee_id | EMP-00101 |
| primary_role | Data Quality Lead |
| secondary_roles | [DGC Member] |
| cost_centres | [CC-DM-001 (0.8), CC-GOV-005 (0.2)] |
| ad_accounts | [shussain] |

## CLI Demo Command
```bash
python -m runtimes.cli unearth employee shared/sample_data/output/employees_dirty.csv
```

## Related Use Cases
- [UC-E01](UC-E01_multi_system_identity_merge.md) — Base identity merge before role assignment
- [UC-XD02](../08_cross_domain_pairs/UC-XD02_asset_location_employee_triangle.md) — Cross-domain: assets assigned to multi-role employees
