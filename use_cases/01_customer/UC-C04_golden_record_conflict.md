# UC-C04: Golden Record Conflict — Address Field Disagreement

## Summary
Three source systems agree a customer exists but disagree on their current city. CRM shows Dubai (last updated 2 years ago), ECOMM shows Abu Dhabi (updated 6 months ago), and the LOYALTY system shows London (from a one-time international order). Survivorship cannot simply pick the most recent — recency alone is misleading when a London address came from a transactional event, not a profile update. AURUM's trust-weighted, context-aware survivorship handles this correctly.

## Domain
Customer

## AURUM Stage(s)
REFINE · UNFURL · MARK

## Business Impact
- Incorrect city in the golden record breaks geo-targeted marketing, store assignment, and delivery routing
- Tax jurisdiction errors if country is also wrong — VAT treatment differs UAE vs UK
- Personalisation engines show wrong regional promotions

## Scenario Setup
Chen Wang is a Dubai-based B2B customer. She placed a one-time order to London for a UK colleague (billing to her UAE account, shipping to London). The LOYALTY system captured London as her city from that order's shipping address — never her home city. CRM hasn't been updated since she moved from Dubai to Abu Dhabi 6 months ago. ECOMM has the latest accurate home address.

## Example Records

| field | CRM-00789 | ECOMM-00445 | LOYALTY-00201 |
|-------|-----------|-------------|---------------|
| city | Dubai | Abu Dhabi | London |
| country | UAE | UAE | UK |
| last_updated | 2024-01-15 | 2024-11-03 | 2024-09-22 |
| address_type | home | home | shipping |

## AURUM Pipeline Walk-Through

**ASSAY** — All three records ingest. Schema inspector notes `address_type` field exists in ECOMM and LOYALTY but not CRM — mapped to canonical schema with null for CRM.

**UNEARTH** — Linked-tuple geography validator: LOYALTY `(London, UK)` is a valid linked pair. ECOMM `(Abu Dhabi, UAE)` valid. CRM `(Dubai, UAE)` valid. No frankenrecords. But cross-record city disagreement is flagged.

**REFINE** — Match cluster formed (same email/phone across all three). Survivorship:
- `address_type = shipping` on LOYALTY record → deprioritised for home address fields
- ECOMM has highest recency for home address AND `address_type = home` → wins
- CRM Dubai suppressed (older + no address_type signal)
- LOYALTY London suppressed (address_type = shipping)
- `FIELD_CONFLICT` event logged for steward visibility

**UNFURL** — Golden record: `city: Abu Dhabi`, `country: UAE`. LOYALTY shipping address retained as `secondary_address` in the extended record.

**MARK** — `FIELD_CONFLICT(city: Dubai/Abu Dhabi/London → Abu Dhabi, rule=address_type+recency)` logged. Full audit trail available.

## Stewardship Decision Point
AURUM resolves automatically but flags the London address because country switched from UAE to UK — a significant jurisdiction change. Steward confirms: shipping address, not home. No intervention needed. Audit event closed.

## Expected Golden Record

| field | golden_value | source | confidence |
|-------|-------------|--------|------------|
| city | Abu Dhabi | ECOMM | 0.91 |
| country | UAE | ECOMM | 0.94 |
| address_type | home | ECOMM | 0.95 |
| secondary_city | London | LOYALTY (shipping) | — |

## CLI Demo Command
```bash
python -m runtimes.cli demo
```

## Related Use Cases
- [UC-C02](UC-C02_cross_channel_merge.md) — Conflicting loyalty tiers across channels
- [UC-L04](../05_location/UC-L04_address_standardisation.md) — Address standardisation at the location domain level
