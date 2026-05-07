# UC-A04: Serial Number Deduplication

## Summary
Two asset records for "HP Laptop" share the same serial number `SN-HP-88234` but have different asset tags (AST-0401 in CMDB, AST-0402 in FM). One is a genuine duplicate entry. The other possibility — more alarming — is that someone swapped the laptop and the FM team registered it as a new asset without retiring the old one. AURUM flags the serial number collision for urgent steward investigation.

## Domain
Asset

## AURUM Stage(s)
ASSAY · REFINE

## Business Impact
- Duplicate asset record inflates the fixed asset count and book value
- If it's an unreported swap: possible theft or undocumented disposal
- Software license compliance: a single-device license may be counted twice
- Warranty claims: two warranty claims filed for one physical unit

## Scenario Setup
CMDB registered `AST-0401` (HP Laptop, serial `SN-HP-88234`) in January 2024. In August 2024, a new joinee was set up — FM created `AST-0402` (HP Laptop, same serial). The IT provisioning team likely re-imaged and redeployed the same physical laptop without retiring the old asset record.

## Example Records

| field | CMDB-0401 | FM-0402 |
|-------|-----------|---------|
| asset_tag | AST-0401 | AST-0402 |
| serial_number | SN-HP-88234 | SN-HP-88234 |
| description | HP Laptop | HP Laptop |
| assigned_to | sara.johnson | lena.fischer |
| lifecycle_state | Active | Active |
| purchase_date | 2023-03-10 | 2023-03-10 |
| location_id | LOC-001 | LOC-007 |

## AURUM Pipeline Walk-Through

**ASSAY** — Schema inspector: `serial_number` cardinality check — `SN-HP-88234` appears twice. Flagged as `SERIAL_COLLISION`.

**UNEARTH** — Asset profiler serial number uniqueness rule: serial numbers must be globally unique. `SN-HP-88234` appears on two records with different asset tags and different assigned users → HIGH severity DQ flag.

**REFINE** — Serial number exact match → MATCH score 1.0. BUT: different asset tags, different assigned_to, different locations. Cluster flagged as `SUSPECTED_DUPLICATE` with `review_priority: HIGH`. Not auto-merged — steward must decide.

## Stewardship Decision Point
Tariq (Security & Compliance) and Jin (Steward) investigate jointly:
- Is this a genuine duplicate entry → merge and retire AST-0402
- Was the laptop redeployed without retiring the old record → retire AST-0401, update AST-0402 as the active record
- Was the laptop stolen and replaced → police report, insurance claim, write-off AST-0401

## Expected Golden Record
Determined by steward investigation. Most likely: `AST-0401` retired (`lifecycle_state: Retired`, `disposal_reason: REDEPLOYED`), `AST-0402` updated as active record with `assigned_to: lena.fischer`.

## CLI Demo Command
```bash
python -m runtimes.cli unearth asset shared/sample_data/output/assets_dirty.csv
```

## Related Use Cases
- [UC-A01](UC-A01_lifecycle_state_conflict.md) — Lifecycle state conflict on the same asset
- [UC-A05](UC-A05_maintenance_lineage_break.md) — Lineage break when asset history is split across two records
