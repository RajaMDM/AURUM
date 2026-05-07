# UC-XD02: Asset × Location × Employee — The Ownership Triangle

## Domains
Asset · Location · Employee

## Summary
Every asset must have a **location** (where it physically is) and an **owner/assignee** (which employee is responsible for it). But after MDM runs independently on each domain, the foreign keys break:
- Asset `AST-0301` references `location_id: LOC-001` — but LOC-001 was merged into `GLD-LOC-0045` (Dubai Mall golden record)
- Asset `AST-0301` references `assigned_to: EMP-00512` — but that employee (Lena) left and was re-hired as `EMP-00892` (new golden ID)
- The triangle is broken at two joints simultaneously

This is the most common cross-domain MDM failure pattern in enterprise environments: asset registers that become meaningless because their references decay.

## Business Impact
- Physical audit: auditor scans asset tag, system shows location "LOC-001" — doesn't exist in the location master → audit fail
- IT access deprovisioning: when Lena left (EMP-00512 inactive), the asset assignment wasn't cleared — risk that an ex-employee's assigned laptop was never retrieved
- Insurance: assets must be at declared locations — stale location_id means wrong insurance coverage
- ISO 55000 / ITIL asset management: all three attributes (asset, location, owner) must be resolvable at any time

## Scenario Setup
- **Asset:** `AST-0301` (HP Laptop), `location_id: LOC-001`, `assigned_to: EMP-00512`
- **Location MDM result:** `LOC-001` → merged into `GLD-LOC-0045` (Dubai Mall)
- **Employee MDM result:** `EMP-00512` (Lena, leaver) → `EMP-00892` (Lena, rehire golden record)
- Asset record still has old foreign keys — MDM ran but didn't push the cross-domain ID updates

## AURUM Pipeline Walk-Through

**Asset ASSAY** — Asset ingested with `location_id: LOC-001`, `assigned_to: EMP-00512`.

**Cross-Domain UNEARTH** — Referential integrity check:
- `LOC-001` → look up in Location golden record table → resolves to `GLD-LOC-0045` ✓ (merge exists)
- `EMP-00512` → look up in Employee golden record table → status=Inactive, successor=`EMP-00892` ✓ (rehire exists)
- Both foreign keys are stale but resolvable — flagged as `STALE_REFERENCE`, not broken

**Cross-Domain REFINE** — Asset record updated:
- `location_id: LOC-001` → `golden_location_id: GLD-LOC-0045`
- `assigned_to: EMP-00512` → `golden_employee_id: GLD-EMP-00892` (rehire record)
- Original IDs retained as `source_location_id` and `source_employee_id` for audit

**UNFURL** — Asset golden record published with all three domains correctly linked. IT helpdesk system receives updated asset-employee assignment — confirms asset was returned on Lena's first departure and re-issued on rehire.

**MARK** — `CROSS_DOMAIN_REANCHOR(AST-0301: location LOC-001→GLD-LOC-0045, employee EMP-00512→GLD-EMP-00892)` logged.

## The Triangle Validated

```
GLD-ASSET-0301 (HP Laptop)
    │
    ├── location_id ──▶ GLD-LOC-0045 (Dubai Mall Store)
    │                       └── parent: LOC-R03 (Downtown Dubai)
    │
    └── assigned_to ──▶ GLD-EMP-00892 (Lena, active)
                            └── department: Data Integration
                            └── cost_centre: CC-INT-001
```

## Stewardship Decision Point
Jin (Steward) validates the employee assignment: Lena rejoined — is she still using this laptop? Confirmed yes. Asset is correctly assigned. Location: Lena works from Dubai Mall office — location confirmed.

## CLI Demo Command
```bash
python -m runtimes.cli demo
```

## Related Use Cases
- [UC-A02](../04_asset/UC-A02_orphaned_asset_detection.md) — Orphaned assets with no location or owner
- [UC-E04](../06_employee/UC-E04_leaver_rehire_detection.md) — Leaver-rehire detection (one side of this triangle)
- [UC-L03](../05_location/UC-L03_store_warehouse_duplicate.md) — Location merge that creates stale references
