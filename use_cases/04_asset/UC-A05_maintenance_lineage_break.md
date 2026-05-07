# UC-A05: Maintenance Lineage Break

## Summary
An HVAC unit (AST-0501) has been serviced four times over three years. The first two services are logged against the original asset record. After a CMDB migration, the asset was re-created with a new asset tag (`AST-0501-NEW`) and the maintenance history wasn't migrated — the lineage is broken. Now the next service engineer has no visibility into previous work: they don't know which parts were replaced, what warranty remains, or whether a recurring fault is present.

## Domain
Asset

## AURUM Stage(s)
MARK · UNFURL

## Business Impact
- Maintenance engineer replaces a part that was replaced 6 months ago — duplicate spend
- Warranty claim rejected because the service history doesn't show the original installation date
- Recurring fault goes undetected — equipment fails catastrophically
- Facilities compliance audit: cannot demonstrate maintenance schedule adherence for fire safety equipment

## Scenario Setup
`AST-0501` (HVAC Unit, serial `SN-HVAC-2201`) has 4 maintenance events in the FM system against the old asset tag. Post-migration, the CMDB created `AST-0501-NEW` with the same serial number. All future maintenance is logged against the new tag. AURUM's MARK stage detects the serial number match and proposes a lineage bridge.

## Example Records

**Old record (FM, pre-migration):**

| field | value |
|-------|-------|
| asset_tag | AST-0501 |
| serial_number | SN-HVAC-2201 |
| maintenance_events | 4 events (Jan 2022, Jun 2022, Jan 2023, Jul 2023) |
| lifecycle_state | Retired (migration close-out) |

**New record (CMDB, post-migration):**

| field | value |
|-------|-------|
| asset_tag | AST-0501-NEW |
| serial_number | SN-HVAC-2201 |
| maintenance_events | 0 |
| lifecycle_state | Active |

## AURUM Pipeline Walk-Through

**ASSAY** — Both records ingest. Serial number `SN-HVAC-2201` matches across old (Retired) and new (Active) records.

**UNEARTH** — Asset profiler: `AST-0501-NEW` has zero maintenance history but purchase_date = 2021 → anomaly: 3-year-old asset with no maintenance history is statistically improbable for HVAC.

**REFINE** — Serial number match links old and new records. `AST-0501` is Retired, `AST-0501-NEW` is Active → this is a LINEAGE_CONTINUATION, not a duplicate. AURUM proposes bridging the lineage.

**UNFURL** — Golden record `GLD-ASSET-0501`: all maintenance events migrated from `AST-0501` history into the active record's lineage. Maintenance history now complete: 4 historical + ongoing.

**MARK** — `LINEAGE_BRIDGE(AST-0501 → AST-0501-NEW, serial=SN-HVAC-2201, events_migrated=4)` logged. Full audit trail preserved.

## Stewardship Decision Point
Facilities manager confirms the bridge: it's the same physical unit. Approves the lineage merge. Next service engineer now sees the complete 3-year maintenance history.

## Expected Golden Record
`GLD-ASSET-0501`: `asset_tag: AST-0501-NEW`, `serial_number: SN-HVAC-2201`, `lifecycle_state: Active`, `maintenance_event_count: 4`, `lineage_source: [AST-0501, AST-0501-NEW]`.

## CLI Demo Command
```bash
python -m runtimes.cli demo
```

## Related Use Cases
- [UC-A04](UC-A04_serial_number_deduplication.md) — Serial number collision (similar detection path, different resolution)
- [UC-C05](../01_customer/UC-C05_lineage_audit_trail.md) — Lineage audit trail pattern in the Customer domain
