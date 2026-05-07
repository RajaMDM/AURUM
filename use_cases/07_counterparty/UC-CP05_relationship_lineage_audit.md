# UC-CP05: Relationship Lineage Audit

## Summary
Regulators require the company to demonstrate, for any counterparty, the complete history of the relationship: when it started, what roles it has played, what transactions occurred, who approved onboarding, what screening results were recorded, and whether any data changes were made to the counterparty record — and by whom. AURUM's MARK stage provides this full provenance on demand.

## Domain
Counterparty

## AURUM Stage(s)
MARK · UNFURL

## Business Impact
- Regulatory audit failure if provenance cannot be demonstrated — UAE CBUAE examination findings
- FATF Travel Rule: financial institutions must demonstrate CDD (Customer Due Diligence) records for all counterparties
- Litigation: in a dispute, the counterparty's record history is evidence — immutable lineage is essential
- Data Subject Access Request: financial counterparties have data rights — lineage enables accurate SARs

## Scenario Setup
The UAE Central Bank examiner asks: "For counterparty Standard Chartered PLC — show us the complete record of your data management decisions, screening results, and who approved what, from onboarding to today." The relationship is 6 years old, spans two merges (when 4 duplicate records were consolidated), a jurisdiction correction, and two sanctions screenings.

## Example Lineage Timeline

| timestamp | event_type | actor | detail |
|-----------|-----------|-------|--------|
| 2018-03-01 | ONBOARDED | Nadia (Governance) | CP-200 created, CDD documentation attached |
| 2019-11-01 | DUPLICATE_CREATED | System | CP-202 (TREASURY) created — not yet linked |
| 2020-07-15 | DUPLICATE_CREATED | System | CP-201 (CRM) created — not yet linked |
| 2021-02-28 | DUPLICATE_CREATED | System | CP-203 (COMPLIANCE) created |
| 2022-04-10 | SCREENED | Tariq (Security) | OFAC, UN, EU — all CLEAR |
| 2023-08-15 | DEDUPLICATION | AURUM REFINE | 4 records merged → GLD-CP-0200, approved by Nadia |
| 2023-08-15 | JURISDICTION_CORRECTED | AURUM MARK | COMPLIANCE jurisdiction UAE → UK, Tariq confirmed |
| 2024-01-20 | SCREENED | Tariq (Security) | OFAC, UN, EU — all CLEAR |
| 2024-09-01 | DUAL_ROLE_LINKED | AURUM REFINE | Linked to GLD-CUST-00445 (customer role added) |

## AURUM Pipeline Walk-Through

**ASSAY** — Every ingestion event logged with source, timestamp, field mapping decisions.

**UNEARTH** — Every DQ rule firing logged against the record.

**REFINE** — Every match decision, merge approval, survivorship decision logged with actor.

**UNFURL** — Every publication and reverse sync logged.

**MARK** — Central lineage store aggregates all events by `golden_id`. Queryable by: counterparty, date range, event type, actor, or decision outcome. Exportable as PDF/JSON for regulatory submission.

## Stewardship Decision Point
No decision needed at query time — the lineage was built continuously. The examiner's request is answered by a lineage query in seconds. Nadia exports the report as a structured JSON for the regulatory response package.

## Expected Output
```json
{
  "golden_id": "GLD-CP-0200",
  "legal_name": "Standard Chartered PLC",
  "relationship_since": "2018-03-01",
  "total_events": 9,
  "screening_results": ["CLEAR 2022-04", "CLEAR 2024-01"],
  "data_changes": ["jurisdiction corrected 2023-08", "4 duplicates merged 2023-08"],
  "current_roles": ["Vendor", "Customer"],
  "approved_by": ["Nadia Al-Hassan", "Tariq Al-Rashid"]
}
```

## CLI Demo Command
```bash
python -m runtimes.cli demo
# Lineage events shown in MARK stage output
```

## Related Use Cases
- [UC-CP01](UC-CP01_dual_role_detection.md) — Dual role that was detected and linked
- [UC-C05](../01_customer/UC-C05_lineage_audit_trail.md) — Customer domain equivalent
- [UC-GS01](../09_grand_scenario/UC-GS01_new_store_opening.md) — Grand scenario where full lineage is built across all 7 domains
