# Employee Domain — Use Cases

The **Employee domain** mastering challenge is identity merge across HRMS, Active Directory, Payroll, and ERP — systems that often disagree on name spelling, employee ID format, department naming, and job title conventions. Org hierarchy integrity (self-manager loops, missing managers) and lifecycle events (leavers, rehires, multi-role assignments) add significant complexity.

## Use Cases

| Code | Title | Complexity | Key Stages |
|------|-------|-----------|------------|
| [UC-E01](UC-E01_multi_system_identity_merge.md) | Multi-System Identity Merge | Medium | ASSAY, REFINE, UNFURL |
| [UC-E02](UC-E02_org_hierarchy_change.md) | Org Hierarchy Change — Reorg Impact | High | REFINE, UNFURL, MARK |
| [UC-E03](UC-E03_multi_role_assignment.md) | Multi-Role Assignment | Medium | REFINE, UNFURL |
| [UC-E04](UC-E04_leaver_rehire_detection.md) | Leaver-Rehire Detection | High | ASSAY, REFINE, MARK |
| [UC-E05](UC-E05_cost_centre_realignment.md) | Cost Centre Realignment | Medium | REFINE, UNFURL, MARK |
