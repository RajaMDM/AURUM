# UC-CP03: Legal Entity Deduplication

## Summary
"Standard Chartered Bank" appears four times: as "Standard Chartered PLC" (LEGAL), "StanChart UAE" (CRM), "SC Bank" (TREASURY), and "Standard Chartered Bank UAE" (COMPLIANCE). All four are used for different transactions. Payments to StanChart go to the right bank, but audit trails reference four different entity names — making counterparty exposure reporting impossible and relationship management fragmented.

## Domain
Counterparty

## AURUM Stage(s)
REFINE · UNFURL

## Business Impact
- Counterparty exposure report shows 4 lines for one bank — exposure appears fragmented
- Relationship manager doesn't see total business value with the counterparty
- Regulatory: consolidated counterparty exposure limits (Basel III large exposure rules) must be calculated at legal entity level — fragmented records cause limit breaches to go undetected
- Audit: four different names on transaction records create reconciliation nightmares

## Scenario Setup
Four records across four systems, all representing the same legal entity (Standard Chartered PLC, LEI: `RILFO74KP1CM8P6PCT96`). Each system created its own record because there was no centralised counterparty register to search first.

## Example Records

| field | LEGAL CP-200 | CRM CP-201 | TREASURY CP-202 | COMPLIANCE CP-203 |
|-------|-------------|-----------|----------------|------------------|
| legal_name | Standard Chartered PLC | StanChart UAE | SC Bank | Standard Chartered Bank UAE |
| lei_code | RILFO74KP1CM8P6PCT96 | | RILFO74KP1CM8P6PCT96 | RILFO74KP1CM |
| jurisdiction | UK | UAE | UAE | UAE |
| relationship_start | 2018-03-01 | 2020-07-15 | 2019-11-01 | 2021-02-28 |

## AURUM Pipeline Walk-Through

**ASSAY** — Four records ingest. LEI present on 2 records, partial on 1, missing on 1.

**UNEARTH** — Counterparty profiler: LEI exact match on LEGAL and TREASURY → `DUPLICATE_CANDIDATE`. COMPLIANCE has partial LEI (12 chars, truncated). CRM has no LEI — name similarity to others flagged.

**REFINE** — LEI anchor: LEGAL + TREASURY cluster (score 1.0). Name similarity: `Standard Chartered PLC` vs `Standard Chartered Bank UAE` = 0.86 → COMPLIANCE added to cluster (score 0.88). `StanChart UAE` = 0.79 → CRM added (above 0.75 threshold, flagged for review). All four in one cluster.

Survivorship: LEGAL record wins for `legal_name` (most authoritative, matches GLEIF registry). Jurisdiction: PLC is a UK legal entity — `jurisdiction: UK` is correct; UAE is where they operate (retained as `operating_jurisdiction`). All four relationship start dates retained in a timeline.

**UNFURL** — Single golden counterparty: `GLD-CP-0200`, `legal_name: Standard Chartered PLC`, `short_names: [StanChart UAE, SC Bank]`, `lei_code: RILFO74KP1CM8P6PCT96`.

## Stewardship Decision Point
Nadia (Governance) confirms: Standard Chartered PLC is the correct parent legal entity; "UAE" variants are operating branches (not separate legal entities under Basel III). The single golden record is authoritative for all exposure calculations.

## Expected Golden Record

| field | golden_value | source |
|-------|-------------|--------|
| legal_name | Standard Chartered PLC | LEGAL (GLEIF-verified) |
| lei_code | RILFO74KP1CM8P6PCT96 | LEGAL/TREASURY |
| jurisdiction | UK | LEGAL |
| operating_jurisdiction | UAE | CRM/TREASURY/COMPLIANCE |

## CLI Demo Command
```bash
python -m runtimes.cli unearth counterparty shared/sample_data/output/counterparties_dirty.csv
```

## Related Use Cases
- [UC-CP01](UC-CP01_dual_role_detection.md) — Dual-role detection after deduplication
- [UC-V02](../03_vendor/UC-V02_group_subsidiary_hierarchy.md) — Group/subsidiary hierarchy (similar pattern)
