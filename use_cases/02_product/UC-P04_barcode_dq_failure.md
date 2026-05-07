# UC-P04: Barcode DQ Failure — Invalid EAN/UPC

## Summary
15% of product records arrive from a new marketplace integration with missing or malformed barcodes — some are 11 digits (should be 12 for UPC or 13 for EAN), some have non-numeric characters, and some are blank. Barcodes are the primary physical identity for products at the point of sale and in the warehouse. Corrupt barcodes mean scan failures at checkout, receiving dock errors, and inventory discrepancies.

## Domain
Product

## AURUM Stage(s)
ASSAY · UNEARTH

## Business Impact
- POS barcode scanner failures — cashiers must manually key in prices — checkout slowdowns
- WMS receiving dock scan failures — inbound stock doesn't register automatically
- Loss prevention: unscanned items may leave without being recorded
- Regulatory: some jurisdictions require valid GTIN on product labels

## Scenario Setup
A marketplace integration delivers 120 product records. Barcode issues found:
- 8 records: blank barcode
- 5 records: 11-digit barcode (EAN-13 requires 13 digits, UPC-A requires 12)
- 3 records: barcode contains letters (`69012AB567890`)
- 2 records: barcode is all zeros (`0000000000000`) — placeholder value

## Example Records

| sku | name | barcode | issue |
|-----|------|---------|-------|
| SKU-0201 | Coffee Blend B | | Missing |
| SKU-0202 | Wireless Mouse | 69012345678 | 11 digits (too short) |
| SKU-0203 | USB Hub | 69012AB567890 | Non-numeric |
| SKU-0204 | Laptop Stand | 0000000000000 | Placeholder zeros |
| SKU-0205 | Keyboard | 6901234567890 | Valid EAN-13 ✓ |

## AURUM Pipeline Walk-Through

**ASSAY** — Schema inspector: `barcode` null rate = 6.7% on this batch. Cardinality check: `0000000000000` appears 2 times — placeholder pattern detected.

**UNEARTH** — Product profiler barcode DQ rules:
- `barcode_length`: must be 12 (UPC-A) or 13 (EAN-13) digits — 5 failures
- `barcode_numeric`: must match `^\d+$` — 3 failures
- `barcode_placeholder`: `0000000000000` pattern → 2 flagged
- `barcode_completeness`: 8 nulls flagged
- Total: 18 records with barcode DQ issues, each tagged with specific rule code

**REFINE** — Records with valid barcodes: barcode used as a high-confidence match key. Records with invalid/missing barcodes: barcode excluded from matching; name+brand+category used instead (lower confidence).

**UNFURL** — 18 records published with `dq_flag: barcode_invalid`, quarantine flag for marketplace remediation request.

## Stewardship Decision Point
Steward sends DQ exception report to the marketplace partner. For internal products, steward manually looks up correct barcodes from physical packaging scan or GS1 registry.

## Expected Golden Record
Records with barcode DQ flags: published without barcode field, `barcode_status: REMEDIATION_REQUIRED`.

## CLI Demo Command
```bash
python -m runtimes.cli assay shared/sample_data/output/products_dirty.csv
python -m runtimes.cli unearth product shared/sample_data/output/products_dirty.csv
```

## Related Use Cases
- [UC-P01](UC-P01_sku_deduplication.md) — SKU dedup where barcode is a match key
