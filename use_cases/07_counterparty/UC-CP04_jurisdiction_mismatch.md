# UC-CP04: Jurisdiction Mismatch

## Summary
A counterparty record shows `legal_name: Al Nakheel Banking Group` with `jurisdiction: Bahrain` in the LEGAL system, but `jurisdiction: UAE` in the COMPLIANCE system and `jurisdiction: BH` in TREASURY. The three-way jurisdiction conflict matters enormously: sanctions screening rules, AML risk rating, withholding tax rates, and regulatory reporting format all depend on the correct legal jurisdiction of incorporation — not where they operate.

## Domain
Counterparty

## AURUM Stage(s)
UNEARTH · REFINE

## Business Impact
- Wrong jurisdiction = wrong AML risk rating (Bahrain and UAE have different FATF risk profiles)
- Withholding tax: payments to a Bahrain entity may have different WHT treatment than UAE
- Sanctions screening: OFAC maintains jurisdiction-specific lists — wrong jurisdiction means wrong list is screened
- Regulatory reporting: counterparty's home jurisdiction must be reported correctly to UAE CBUAE

## Scenario Setup
Al Nakheel Banking Group is legally incorporated in Bahrain (correct). The COMPLIANCE system was set up with `UAE` by mistake (the team member confused operating presence with incorporation). TREASURY uses the ISO country code `BH` which is correct but in a different format. The LEGAL system has the narrative name `Bahrain`.

## Example Records

| field | LEGAL CP-301 | COMPLIANCE CP-302 | TREASURY CP-303 |
|-------|-------------|------------------|----------------|
| legal_name | Al Nakheel Banking Group | Al Nakheel Banking Group BSC | Al Nakheel Bank |
| jurisdiction | Bahrain | UAE | BH |
| lei_code | 2138005EXAMPLE00001 | 2138005EXAMPLE00001 | 2138005EXAMPLE00001 |
| role | Counterparty | Counterparty | Banking Partner |

## AURUM Pipeline Walk-Through

**ASSAY** — Three records ingest. LEI matches across all three — same legal entity.

**UNEARTH** — Counterparty profiler jurisdiction rules:
- `jurisdiction_normalise`: `Bahrain` / `BH` / `UAE` — LEI lookup confirms incorporation country = `BH` (Bahrain). `UAE` on COMPLIANCE flagged as `JURISDICTION_MISMATCH`, HIGH severity.
- `jurisdiction_lei_cross_check`: GLEIF registry for this LEI returns `jurisdiction: BH` → COMPLIANCE record is definitively wrong.

**REFINE** — Cluster formed (LEI exact match). Survivorship: LEGAL record + GLEIF validation → `jurisdiction: BH` (Bahrain) wins. COMPLIANCE `UAE` is an error — logged as `DQ_ERROR_CORRECTED`.

**UNFURL** — Golden record: `jurisdiction: BH`. COMPLIANCE system receives correction via reverse sync.

## Stewardship Decision Point
Tariq (Security & Compliance) confirms the correction. Triggers a re-run of sanctions screening with the correct jurisdiction. AML risk rating recalculated. No adverse finding — Al Nakheel Banking Group is not on any relevant list.

## Expected Golden Record

| field | golden_value | source | confidence |
|-------|-------------|--------|------------|
| legal_name | Al Nakheel Banking Group BSC | COMPLIANCE (most formal name) | 0.94 |
| jurisdiction | BH | LEGAL + GLEIF validation | 1.0 |
| lei_code | 2138005EXAMPLE00001 | Consensus | 1.0 |

## CLI Demo Command
```bash
python -m runtimes.cli unearth counterparty shared/sample_data/output/counterparties_dirty.csv
```

## Related Use Cases
- [UC-CP02](UC-CP02_lei_validation_failure.md) — LEI validation (jurisdiction derived from LEI registry)
- [UC-CP03](UC-CP03_legal_entity_deduplication.md) — Deduplication before jurisdiction resolution
