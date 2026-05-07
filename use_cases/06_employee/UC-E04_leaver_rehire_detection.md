# UC-E04: Leaver-Rehire Detection

## Summary
Lena Fischer left the company in January 2023. Her HRMS record was set to `Inactive`. She rejoined in September 2024 as a senior role — and was given a brand new employee ID (`EMP-00892`) by the new HR admin who didn't search for an existing record. Now two records exist for the same person. Her historical service record, previous performance reviews, and original hire date are orphaned on the old record — critical for long-service awards, pension entitlements, and rehire background check compliance.

## Domain
Employee

## AURUM Stage(s)
ASSAY · REFINE · MARK

## Business Impact
- Continuous service calculation wrong — affects long-service award eligibility and statutory leave entitlements
- Pension / end-of-service gratuity (UAE Labour Law Article 51) miscalculated without original hire date
- Background check: rehires may have a reduced check requirement — without detecting the rehire, full cost check is run unnecessarily  
- Rehire policy compliance: some roles have cooling-off periods — undetected rehire may violate policy

## Scenario Setup
Old record: `EMP-00512` (Lena Fischer, Integration Lead, status: Inactive, hire_date: 2020-03-01, leave_date: 2023-01-15). New record: `EMP-00892` (Lena Fischer, Senior Integration Lead, status: Active, hire_date: 2024-09-01). Same name, same email domain, same department.

## Example Records

| field | EMP-00512 (old) | EMP-00892 (new) |
|-------|----------------|----------------|
| first_name | Lena | Lena |
| last_name | Fischer | Fischer |
| email | lena.fischer@company.com | lena.fischer@company.com |
| status | Inactive | Active |
| hire_date | 2020-03-01 | 2024-09-01 |
| department | Data Integration | Integration |
| job_title | Integration Lead | Senior Integration Lead |

## AURUM Pipeline Walk-Through

**ASSAY** — Both records ingest. Email exact match across records with different status (Inactive vs Active) → `REHIRE_CANDIDATE` signal raised immediately.

**UNEARTH** — Employee profiler rehire detection rules:
- `inactive_email_match`: active record email matches an inactive record → HIGH priority flag
- `name_match_inactive`: `Lena Fischer` exact match on inactive record → `PROBABLE_REHIRE`
- `hire_gap`: gap between old leave_date (2023-01-15) and new hire_date (2024-09-01) = 20 months → within rehire detection window

**REFINE** — Cluster formed: `EMP-00512` (Inactive) and `EMP-00892` (Active). Resolution: REHIRE pattern — do NOT merge flat, instead link as a LIFECYCLE_CHAIN: `EMP-00512 → EMP-00892` (predecessor → successor).

**MARK** — `REHIRE_DETECTED(EMP-00512 → EMP-00892, gap=20 months, original_hire=2020-03-01, rehire_date=2024-09-01)` logged. HR compliance notified for background check review.

## Stewardship Decision Point
HR Manager confirms: this is the same person, rehire is approved and documented. Decides: continuous service is NOT counted (company policy: service clock resets on rehire). Historical record linked for reference but `original_service_start` field retained for long-service reference.

## Expected Golden Record
`GLD-EMP-00892` (active record): `hire_date: 2024-09-01`, `predecessor_id: EMP-00512`, `original_hire_date: 2020-03-01`, `rehire: true`, `rehire_gap_months: 20`.

## CLI Demo Command
```bash
python -m runtimes.cli unearth employee shared/sample_data/output/employees_dirty.csv
```

## Related Use Cases
- [UC-E01](UC-E01_multi_system_identity_merge.md) — Standard identity merge (non-rehire)
- [UC-C05](../01_customer/UC-C05_lineage_audit_trail.md) — Lineage chain pattern (customer equivalent)
