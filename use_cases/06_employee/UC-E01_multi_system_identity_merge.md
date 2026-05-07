# UC-E01: Multi-System Identity Merge — Employee Across HRMS, AD, Payroll

## Summary
Arun joined the company in March. HRMS created his record with employee ID `EMP-00445`. Active Directory provisioned him as `amehta` with no employee ID. Payroll imported from a legacy system where he's `Arun K.` with payroll ID `PAY-9921`. Three systems, three identifiers, no link between them. HR analytics, access reviews, and payroll reconciliation all fail when they can't join on a common key.

## Domain
Employee

## AURUM Stage(s)
ASSAY · REFINE · UNFURL

## Business Impact
- Security access review cannot confirm which AD account belongs to which HRMS employee — compliance gap
- Payroll reconciliation fails — can't confirm every HRMS employee has a payroll record and vice versa
- HR analytics (headcount, attrition, cost per hire) based on HRMS miss employees who are in Payroll but not yet HRMS
- Joiner-Mover-Leaver (JML) process breaks: if AD and HRMS aren't linked, leaving employees may retain AD access

## Scenario Setup
Three records for the same physical person across three systems with no shared identifier:

| source | id | name | email | dept |
|--------|-----|------|-------|------|
| HRMS | EMP-00445 | Arun | arun.mehta@company.com | BI & Analytics |
| AD | — | amehta | arun.mehta@company.com | — |
| PAYROLL | PAY-9921 | Arun K. | a.mehta@company.com | Analytics |

## AURUM Pipeline Walk-Through

**ASSAY** — Three records from three schemas. AD record has no employee_id field — mapped to canonical schema with null. Email domain match across HRMS and AD. Payroll has a different email format (`a.mehta` vs `arun.mehta`).

**UNEARTH** — Employee profiler: email format check — `a.mehta@company.com` is valid but differs from HRMS pattern. Department name: `BI & Analytics` vs `Analytics` — similarity 0.79, flagged as possible variant. Name: `Arun` vs `Arun K.` — middle initial present in Payroll only.

**REFINE** — Name similarity: 0.91. Email similarity (normalised domain): HRMS/AD share exact email → strong signal. HRMS+AD cluster first (score 0.97), then PAYROLL added (name+dept, score 0.84). All three in one cluster.

**UNFURL** — Golden employee `GLD-EMP-00445`: `employee_id: EMP-00445`, `ad_account: amehta`, `payroll_id: PAY-9921`. Cross-system IDs stored so any system can find the golden record.

## Stewardship Decision Point
Jin (Steward) confirms the Payroll email (`a.mehta@`) — an old format from the legacy system. Payroll is notified to update to the canonical email. AD account confirmed as belonging to Arun.

## Expected Golden Record

| field | golden_value | source |
|-------|-------------|--------|
| employee_id | EMP-00445 | HRMS |
| ad_account | amehta | AD |
| payroll_id | PAY-9921 | PAYROLL |
| full_name | Arun | HRMS |
| email | arun.mehta@company.com | HRMS/AD |
| department | BI & Analytics | HRMS |

## CLI Demo Command
```bash
python -m runtimes.cli unearth employee shared/sample_data/output/employees_dirty.csv
```

## Related Use Cases
- [UC-E04](UC-E04_leaver_rehire_detection.md) — When the same employee leaves and rejoins
- [UC-XD02](../08_cross_domain_pairs/UC-XD02_asset_location_employee_triangle.md) — Employee linked to Asset and Location
