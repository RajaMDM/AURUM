# UC-C03: DQ Failure — Missing Email and Invalid Phone

## Summary
A batch of 47 customer records ingested from a third-party retail partner arrives with 38% missing emails and phone numbers in a mix of local and international formats that fail validation. Without catching these at UNEARTH, downstream marketing automation sends to null recipients, CRM workflows break, and the golden record inherits garbage. This is a bread-and-butter DQ scenario every MDM team faces at integration time.

## Domain
Customer

## AURUM Stage(s)
ASSAY · UNEARTH

## Business Impact
- Email marketing campaigns fail silently — no error, just zero delivery
- CRM deduplication relies on email as a match key — missing emails cause phantom duplicates
- Regulatory: UAE PDPL and GDPR require contact data accuracy for consent tracking
- Helpdesk workflows that route by phone break for records with invalid numbers

## Scenario Setup
A retail partner migration delivers a CSV with 47 customer records. Quality issues:
- 18 records have blank `email` fields (partner system didn't enforce it)
- 12 records have emails in plain name format (`sara`, `james`) without domain — clearly truncated
- 9 records have phones as local 7-digit numbers (`5012345`) without country code
- 8 records have phones with letters (`+971-5O-1234567` — letter O not digit 0)

## Example Records

| field | Record A | Record B | Record C | Record D |
|-------|----------|----------|----------|----------|
| first_name | Sara | James | Priya | Ahmed |
| last_name | Johnson | Smith | Sharma | Al-Farsi |
| email | | james | priya.sharma@meridian.com | ahmed@meridian.com |
| phone | +971501234567 | 5567890 | +971-5O-9876543 | |
| DQ issue | missing email | truncated email | letter-O in phone | missing phone |

## AURUM Pipeline Walk-Through

**ASSAY** — Schema inspector flags: `email` null rate = 38% (threshold: 10%), cardinality anomaly on `email` (many unique short strings suggesting truncation).

**UNEARTH** — Customer profiler DQ rules fire:
- `email_format`: regex `^[^@]+@[^@]+\.[^@]+$` — 30 failures flagged
- `phone_uae_format`: normalisation attempt fails on `5567890` (no country code) and `+971-5O-9876543` (non-numeric character)
- `completeness_email`: 18 records scored 0 for completeness on email field
- Anomaly detector: short `email` values (`sara`, `james`) scored as high anomaly

**REFINE** — Records with no email AND no phone cannot be reliably matched. AURUM creates singleton clusters and marks them `match_confidence: LOW`. They are not merged with any existing record.

**UNFURL** — DQ report generated: 47 records assessed, 30 email failures, 17 phone failures, 8 records quarantined (too incomplete to publish). 39 records published with DQ flags attached.

**MARK** — Each quarantined record logged with `DQ_QUARANTINE` event and rule codes for steward remediation.

## Stewardship Decision Point
Steward receives a DQ exception report: 8 records quarantined, 22 others published with warnings. Decision: send back to the retail partner for remediation, or manually enrich using a reference lookup (e.g., check the partner's web portal for the customer's email).

## Expected Golden Record
Quarantined records: no golden record published until remediated.
For records with partial data (e.g., email present, phone missing): published with `completeness_score: 0.71` and `dq_flags: [phone_missing]`.

## CLI Demo Command
```bash
python -m runtimes.cli assay shared/sample_data/output/customers_dirty.csv
python -m runtimes.cli unearth customer shared/sample_data/output/customers_dirty.csv
```

## Related Use Cases
- [UC-C01](UC-C01_identity_resolution.md) — Identity resolution after DQ is cleaned
- [UC-C05](UC-C05_lineage_audit_trail.md) — Lineage trail for quarantined then remediated records
