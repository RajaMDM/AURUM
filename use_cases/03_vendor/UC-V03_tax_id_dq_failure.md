# UC-V03: Tax ID DQ Failure

## Summary
UAE VAT TRN (Tax Registration Number) must be exactly 15 digits. A batch of 200 vendor records imported from an ERP migration contains 34 records with TRNs that are truncated, alphanumeric, or null. Filing VAT returns against invalid TRNs creates compliance exposure — the Federal Tax Authority (FTA) will reject submissions, and the company may be liable for the full VAT amount without the input tax credit.

## Domain
Vendor

## AURUM Stage(s)
ASSAY · UNEARTH

## Business Impact
- UAE FTA rejects VAT return submissions referencing invalid supplier TRNs
- Company loses right to claim input VAT credit on those purchases — direct cash loss
- Audit risk: large number of invalid TRNs suggests inadequate vendor onboarding controls
- Sanctions screening failure: TRN is a primary identifier for AML/sanctions checks

## Scenario Setup
ERP migration from legacy system. The legacy system had a 10-character TRN field (pre-UAE VAT era). Post-VAT, TRNs became 15 digits, but the field was never widened — TRNs got truncated on export. Some vendors never registered for VAT (legitimately, if below AED 375,000 threshold) and have null TRNs, which is fine — but needs to be distinguished from missing data.

## Example Records

| vendor_id | legal_name | tax_id | issue |
|-----------|-----------|--------|-------|
| ERP-V201 | Al Safa Trading LLC | TRN10034500 | Truncated (11 chars) |
| ERP-V202 | Gulf Tech FZE | TRN1003AB5670001 | Alphanumeric |
| ERP-V203 | Noor Supplies | | Null — below VAT threshold? |
| ERP-V204 | Dubai Print Co | 100345670001234 | Missing TRN prefix |
| ERP-V205 | Abu Dhabi Catering | 100345670001235 | Missing TRN prefix |

## AURUM Pipeline Walk-Through

**ASSAY** — Schema inspector: `tax_id` null rate = 8% (34/400). Cardinality: several short values detected.

**UNEARTH** — Vendor profiler UAE TRN rules:
- `trn_format`: must match `^TRN\d{12}$` (15 chars total with prefix) — 28 failures
- `trn_numeric`: must be digits only after prefix — 3 failures (alphanumeric)
- `trn_completeness`: null TRN flagged as WARNING (may be legitimate) — 18 records
- Anomaly detector: `tax_id` length anomaly on 11 short-format records

**REFINE** — Vendors with invalid TRN: TRN excluded as match key. Name + country + city used instead (lower confidence matching). Records flagged `match_confidence: MEDIUM`.

**UNFURL** — DQ exception report: 34 records with TRN issues exported for vendor remediation outreach. Published with `dq_flags: [trn_invalid]`.

## Stewardship Decision Point
Two categories of action needed:
1. Truncated/malformed TRNs → contact vendor for correct TRN or look up on FTA portal
2. Null TRNs → determine if vendor is below VAT threshold (legitimate) or just missing data

## Expected Golden Record
Records with valid TRN after remediation: `tax_id: TRN100345670001234`, `trn_verified: true`.
Records below VAT threshold: `tax_id: null`, `vat_exempt: true`, `vat_exempt_reason: BELOW_THRESHOLD`.

## CLI Demo Command
```bash
python -m runtimes.cli unearth vendor shared/sample_data/output/vendors_dirty.csv
```

## Related Use Cases
- [UC-V01](UC-V01_legal_vs_trading_entity.md) — Legal entity resolution (TRN is the anchor)
- [UC-CP02](../07_counterparty/UC-CP02_lei_validation_failure.md) — LEI validation failure (financial counterparty equivalent)
