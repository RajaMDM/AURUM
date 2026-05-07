# UC-C05: Customer Lineage Audit Trail

## Summary
A compliance audit requires proving exactly which source systems contributed to a customer's golden record, what decisions were made during mastering, who approved exceptions, and when each change happened. Without a complete lineage trail, the organisation cannot demonstrate GDPR Article 30 (records of processing) or UAE PDPL compliance. AURUM's MARK stage makes this audit trivially answerable.

## Domain
Customer

## AURUM Stage(s)
MARK · UNFURL

## Business Impact
- Failed compliance audit → regulatory fines (GDPR up to 4% of global revenue)
- Inability to respond to Subject Access Requests (SARs) within mandated timeframes
- Legal exposure when a disputed transaction can't be traced to its source record
- Reputational damage if data provenance cannot be demonstrated

## Scenario Setup
A data subject (James Smith) submits a Subject Access Request under GDPR. The compliance team needs to answer: Where did we get his data? What changes have been made? Has it been shared? Who approved the merge of his three source records? AURUM's lineage tracker has the full answer.

## Example Records
Timeline of lineage events for golden record `GLD-CUST-00023`:

| timestamp | event_type | actor | detail |
|-----------|-----------|-------|--------|
| 2024-03-01T09:12 | INGESTED | ASSAY | CRM-00023 ingested, 12 fields mapped |
| 2024-03-01T09:12 | INGESTED | ASSAY | ECOMM-00156 ingested, 10 fields mapped |
| 2024-03-01T09:13 | DQ_FLAG | UNEARTH | phone format invalid on ECOMM-00156 |
| 2024-03-01T09:13 | MATCHED | REFINE | CRM-00023 + ECOMM-00156 score=0.94 |
| 2024-03-01T09:13 | GOLDEN_ASSEMBLED | REFINE | GLD-CUST-00023 created, trust=0.89 |
| 2024-03-14T11:30 | STEWARD_REVIEW | Jin (Steward) | Approved merge, noted phone remediation |
| 2024-03-14T11:31 | PUBLISHED | UNFURL | GLD-CUST-00023 pushed to CRM, ECOMM |

## AURUM Pipeline Walk-Through

**ASSAY** — Every ingestion event logged: source system, timestamp, record count, field mapping decisions.

**UNEARTH** — Every DQ rule firing logged with rule code, field, value, and severity.

**REFINE** — Every match decision logged: pair, score, threshold, outcome. Every survivorship decision logged: field, competing values, winning value, rule applied.

**UNFURL** — Every publication event logged: target system, timestamp, golden_id, fields sent.

**MARK** — Central lineage store aggregates all events per golden record. Queryable by golden_id, source_id, timestamp range, actor, or event type.

## Stewardship Decision Point
For a SAR response, the steward queries MARK by `source_id = CRM-00023`. Returns full event history in seconds. Steward exports the lineage report as evidence for the compliance team — no manual reconstruction required.

## Expected Golden Record
Not applicable — this use case focuses on the lineage audit output, not the record itself.

**Lineage query output (pseudocode):**
```
GET /lineage?source_id=CRM-00023
→ golden_id: GLD-CUST-00023
→ events: [INGESTED, DQ_FLAG, MATCHED, GOLDEN_ASSEMBLED, STEWARD_REVIEW, PUBLISHED]
→ sources_contributing: [CRM-00023, ECOMM-00156]
→ published_to: [CRM, ECOMM]
→ last_updated: 2024-03-14T11:31
```

## CLI Demo Command
```bash
python -m runtimes.cli demo
# Lineage events printed at the end of the demo output
```

## Related Use Cases
- [UC-C01](UC-C01_identity_resolution.md) — The merge that creates the lineage trail
- [UC-CP05](../07_counterparty/UC-CP05_relationship_lineage_audit.md) — Lineage audit for counterparty relationships
