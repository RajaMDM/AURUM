# UC-CP02: LEI Validation Failure

## Summary
LEI (Legal Entity Identifier) codes follow the ISO 17442 standard: 20 alphanumeric characters, specific check-digit algorithm. A batch of 180 counterparty records from a treasury system migration has 31 records with invalid LEIs — truncated codes, wrong length, failed check digit, or placeholder values. For financial institutions, an invalid LEI means the counterparty cannot be reported to trade repositories under EMIR/MiFID II or UAE CBUAE regulations.

## Domain
Counterparty

## AURUM Stage(s)
ASSAY · UNEARTH

## Business Impact
- Regulatory reporting failure: EMIR trade reporting requires valid LEI for both counterparties — invalid LEI = reportable breach
- UAE CBUAE: financial institutions must maintain valid LEI for all regulated counterparties
- Correspondent banking: SWIFT transaction screening uses LEI — invalid LEI causes payment delays
- Sanctions: LEI is a primary identifier in OFAC/UN sanctions lists — invalid LEI breaks screening

## Scenario Setup
Treasury system migrated from a 18-character legacy identifier to LEI. The migration script padded short codes with zeros (wrong approach — LEI check digit is position-sensitive). Some vendors who self-registered provided placeholder LEIs (`0000000000000000000X`).

## Example Records

| counterparty_id | legal_name | lei_code | issue |
|----------------|-----------|---------|-------|
| CP-00101 | HSBC UAE | 213800EXAMPLEHSBCAE1 | Valid ✓ |
| CP-00102 | Mashreq Bank | 213800MASHREQ000001 | 19 chars (too short) |
| CP-00103 | Emirates NBD | 213800ENBD0000000099 | Wrong check digit |
| CP-00104 | Al Hilal Bank | 00000000000000000001 | Placeholder zeros |
| CP-00105 | Dubai Islamic Bank | DIBUAENBD2024000001X | Non-standard format |

## AURUM Pipeline Walk-Through

**ASSAY** — Schema inspector: `lei_code` values have inconsistent lengths (17–21 chars). Flagged. Cardinality: placeholder zeros pattern detected.

**UNEARTH** — Counterparty profiler LEI rules:
- `lei_length`: must be exactly 20 characters — 8 failures
- `lei_alphanumeric`: must match `^[A-Z0-9]{18}\d{2}$` (18 alphanumeric + 2 digit check) — 12 failures
- `lei_check_digit`: Luhn-mod-97 check digit validation — 6 failures (wrong check digit)
- `lei_placeholder`: all-zeros pattern → 5 flagged
- Total: 31 records with LEI DQ issues

**REFINE** — Records with invalid LEI: LEI excluded as match key. Legal name + jurisdiction used instead (lower confidence). All 31 published with `dq_flags: [lei_invalid]`, `screening_blocked: true`.

## Stewardship Decision Point
Tariq (Security) blocks all 31 from sanctions screening queue until LEIs are corrected. Nadia (Governance) sends remediation requests. Valid LEIs can be looked up on the GLEIF Global LEI Registry (https://www.gleif.org).

## Expected Golden Record
After remediation: `lei_code: 213800MASHREQ000X01Y` (verified from GLEIF), `lei_verified: true`, `lei_verified_date: 2024-11-25`, `screening_blocked: false`.

## CLI Demo Command
```bash
python -m runtimes.cli unearth counterparty shared/sample_data/output/counterparties_dirty.csv
```

## Related Use Cases
- [UC-V03](../03_vendor/UC-V03_tax_id_dq_failure.md) — Tax ID DQ failure (commercial equivalent)
- [UC-CP04](UC-CP04_jurisdiction_mismatch.md) — Jurisdiction mismatch often co-occurs with LEI issues
