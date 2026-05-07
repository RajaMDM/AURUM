# UC-L04: Address Standardisation

## Summary
Location addresses arrive from five source systems in five different formats — some use P.O. Box, some use plot numbers, some use building names, some use abbreviations (St. vs Street, Rd vs Road). None is wrong, but none matches either. Downstream systems (courier APIs, geocoding services, emergency services) need a single standardised address format. AURUM's ASSAY and UNEARTH stages normalise all variants to a canonical address schema.

## Domain
Location

## AURUM Stage(s)
ASSAY · UNEARTH

## Business Impact
- Courier API rejects non-standard address formats — last-mile delivery failures
- Geocoding service returns null for P.O. Box addresses — feeds into the Null Island problem (UC-L02)
- Customer-facing address on invoices/receipts inconsistent per channel — brand and legal risk
- Emergency dispatch systems require standardised address format for response SLA compliance

## Scenario Setup
The same Dubai Mall store address appears as: "Dubai Mall, Financial Centre Road, Downtown Dubai" (CRM), "P.O. Box 112233, Dubai" (ERP), "Fin. Centre Rd, DT Dubai, UAE" (YEXT), "Financial Centre Rd." (FM), "Shop 123, Dubai Mall, DC" (WMS).

## Example Records

| source | address_line1 | city | country |
|--------|--------------|------|---------|
| CRM | Dubai Mall, Financial Centre Road | Downtown Dubai | UAE |
| ERP | P.O. Box 112233 | Dubai | AE |
| YEXT | Fin. Centre Rd, DT Dubai | Dubai | United Arab Emirates |
| FM | Financial Centre Rd. | Dubai | UAE |
| WMS | Shop 123, Dubai Mall, DC | Dubai | AE |

## AURUM Pipeline Walk-Through

**ASSAY** — Five address variants ingested. Schema inspector: `address_line1` has high cardinality (5 unique values for the same location). `country` has 3 variants for the same country.

**UNEARTH** — Location profiler address rules:
- `country_code_normalise`: `AE` / `UAE` / `United Arab Emirates` → all normalised to `UAE` (ISO 3166-1 alpha-3)
- `pobox_flag`: ERP record is P.O. Box only → flagged as `ADDRESS_TYPE: POBOX`, not a physical address
- `address_abbreviation`: `Rd.` → `Road`, `St.` → `Street`, `DT` → `Downtown`, `Fin.` → `Financial`
- `city_normalise`: `Downtown Dubai` → `Dubai` (suburb, not a separate city in the canonical list)

**REFINE** — After normalisation, all five addresses resolve to: `Financial Centre Road, Downtown Dubai, Dubai, UAE`. Cluster formed. Survivorship: CRM address (most complete) as primary, P.O. Box retained as `alt_address`.

## Stewardship Decision Point
Lena (Integration) reviews the P.O. Box — some courier integrations need it. Confirmed: retain P.O. Box as `alt_address`, not as primary.

## Expected Golden Record

| field | golden_value |
|-------|-------------|
| address_line1 | Financial Centre Road |
| address_line2 | Dubai Mall |
| city | Dubai |
| district | Downtown Dubai |
| country | UAE |
| postal_code | 112233 |
| alt_address | P.O. Box 112233, Dubai, UAE |

## CLI Demo Command
```bash
python -m runtimes.cli assay shared/sample_data/output/locations_dirty.csv
python -m runtimes.cli unearth location shared/sample_data/output/locations_dirty.csv
```

## Related Use Cases
- [UC-L02](UC-L02_geocoding_drift.md) — Geocoding drift caused by non-standard addresses
