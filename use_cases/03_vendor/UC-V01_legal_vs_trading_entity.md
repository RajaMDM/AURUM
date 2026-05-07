# UC-V01: Legal vs Trading Entity Resolution

## Summary
"Falco Tech Solutions LLC" is the legal entity registered with the UAE Ministry of Economy. It trades under the name "FTS" in most contracts and "FalcoTech" in the ERP. Procurement created three vendor records — one per name. Payments now split across three vendor accounts, causing AP reconciliation failures and incorrect 1099/WHT reporting against the wrong legal entity. AURUM resolves legal vs trading entity and links them correctly.

## Domain
Vendor

## AURUM Stage(s)
ASSAY · REFINE · UNFURL

## Business Impact
- Split payment runs — partial payments go to different vendor accounts, creating overdue disputes
- Tax withholding calculated against trading name instead of legal entity — regulatory exposure
- Supplier scorecards fragmented — can't see total spend or performance for the real entity
- Year-end audit: auditors flag multiple vendor codes for the same supplier

## Scenario Setup
Three records exist in different source systems for the same vendor:

| source | name | type |
|--------|------|------|
| ERP | FalcoTech | Trading name |
| PROCUREMENT | FTS | Short name |
| AP | Falco Tech Solutions LLC | Legal name |
| SUPPLIER_PORTAL | Falco Tech Solutions | Informal |

## Example Records

| field | ERP-V001 | PROC-V045 | AP-V012 | PORTAL-V089 |
|-------|----------|-----------|---------|-------------|
| legal_name | | | Falco Tech Solutions LLC | Falco Tech Solutions |
| trading_name | FalcoTech | FTS | | |
| tax_id | TRN100234567 | | TRN100234567 | TRN1002345 |
| country | UAE | AE | United Arab Emirates | UAE |
| payment_terms | Net 30 | Net 30 | Net 30 | |

## AURUM Pipeline Walk-Through

**ASSAY** — Four vendor records ingest. Schema maps `legal_name` and `trading_name` to canonical schema.

**UNEARTH** — Vendor profiler: `TRN1002345` (10 chars) vs `TRN100234567` (12 chars) — UAE TRN must be 15 chars. Both fail TRN format rule. Cross-record: two records share matching partial TRN → likely same entity.

**REFINE** — Matcher uses TRN as primary match key (partial match via prefix). Name similarity: `FalcoTech` vs `Falco Tech Solutions` = 0.84. Cluster formed. Survivorship: AP record (`Falco Tech Solutions LLC`) wins as legal_name (most specific, matches Companies Registry format). Trading names consolidated into `trading_names[]` array.

**UNFURL** — Single golden vendor: `GLD-VEND-0012`, `legal_name: Falco Tech Solutions LLC`, `trading_names: [FalcoTech, FTS, Falco Tech Solutions]`.

## Stewardship Decision Point
Steward confirms the TRN — AP has a truncated version, ERP has the full one. AP record updated. Steward also confirms the legal entity type (LLC) from the trade licence.

## Expected Golden Record

| field | golden_value | source | confidence |
|-------|-------------|--------|------------|
| legal_name | Falco Tech Solutions LLC | AP | 0.98 |
| trading_name | FalcoTech | ERP | 0.92 |
| tax_id | TRN100234567003 | ERP (steward-verified) | 1.0 |
| country | UAE | Consensus | 0.99 |
| payment_terms | Net 30 | Consensus | 1.0 |

## CLI Demo Command
```bash
python -m runtimes.cli unearth vendor shared/sample_data/output/vendors_dirty.csv
```

## Related Use Cases
- [UC-V02](UC-V02_group_subsidiary_hierarchy.md) — Group/subsidiary hierarchy
- [UC-V04](UC-V04_duplicate_vendor_detection.md) — Duplicate detection without TRN anchor
