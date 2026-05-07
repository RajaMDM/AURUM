# UC-C01: Customer Identity Resolution Across Source Systems

## Summary
A single customer — say, Priya Sharma — exists in three source systems (CRM, ECOMM, LOYALTY) with slightly different name spellings, phone formats, and email casing. Without identity resolution, downstream analytics counts her as three separate customers, inflating the customer base, corrupting CLV calculations, and triggering duplicate marketing campaigns. This is the core MDM problem AURUM is built to solve.

## Domain
Customer

## AURUM Stage(s)
ASSAY · UNEARTH · REFINE · UNFURL · MARK

## Business Impact
- Marketing sends the same promotion 3× to the same person — brand damage and regulatory risk (GDPR/UAE PDPL repeat contact)
- CLV, churn, and loyalty tier calculations are wrong
- Customer service agents see fragmented history — no single view
- Loyalty points split across phantom accounts

## Scenario Setup
Priya Sharma registered via the company website (ECOMM), was later added manually to the CRM by a sales rep, and earned loyalty points via the LOYALTY program. Each system captured her data independently with format differences:
- CRM has `Priya Sharma`, UAE phone `+971501234567`, email `priya.sharma@meridian.com`
- ECOMM has `PRIYA SHARMA`, phone `00971-50-1234567`, email `PRIYA.SHARMA@meridian.com`
- LOYALTY has `priya sharma`, phone blank, email `priyasharma@meridian.com`

## Example Records

| field | CRM-00101 | ECOMM-00234 | LOYALTY-00089 |
|-------|-----------|-------------|---------------|
| first_name | Priya | PRIYA | priya |
| last_name | Sharma | SHARMA | sharma |
| email | priya.sharma@meridian.com | PRIYA.SHARMA@meridian.com | priyasharma@meridian.com |
| phone | +971501234567 | 00971-50-1234567 | |
| city | Dubai | Dubai | dubai |
| country | UAE | AE | United Arab Emirates |
| loyalty_tier | | Gold | Gold |

## AURUM Pipeline Walk-Through

**ASSAY** — Schema inspector detects 3 source schemas. Maps all to canonical Customer schema. Flags phone format heterogeneity (3 formats across sources) and email case inconsistency.

**UNEARTH** — Customer profiler fires:
- Email format rule: `PRIYA.SHARMA@meridian.com` fails lowercase check
- Phone format rule: `00971-50-1234567` normalises to `+971501234567`
- Completeness rule: LOYALTY record missing phone — flagged as incomplete
- Anomaly detector: LOYALTY email (`priyasharma@meridian.com` vs `priya.sharma@`) flagged as moderate anomaly

**REFINE** — Matcher scores:
- CRM vs ECOMM: name similarity 0.97, email (normalised) 1.0 → MATCH (score 0.98)
- CRM vs LOYALTY: name similarity 0.95, email similarity 0.72 → PROBABLE MATCH (score 0.81, above 0.75 threshold)
- All three collapsed into one cluster. Survivorship: CRM email (most complete), ECOMM phone (only valid one), LOYALTY loyalty_tier.

**UNFURL** — Golden record published with `golden_id: GLD-CUST-00101`, trust score 0.87.

**MARK** — Lineage events logged: `MATCHED(CRM-00101, ECOMM-00234)`, `MATCHED(CRM-00101, LOYALTY-00089)`, `GOLDEN_ASSEMBLED(GLD-CUST-00101)`. Reverse sync plan: push `golden_id` back to all 3 sources.

## Stewardship Decision Point
LOYALTY email (`priyasharma@meridian.com`) differs enough from the CRM/ECOMM pattern that AURUM flags it for steward review rather than auto-merging silently. The steward sees the three records side-by-side and confirms the merge.

## Expected Golden Record

| field | golden_value | source | confidence |
|-------|-------------|--------|------------|
| first_name | Priya | CRM | 0.95 |
| last_name | Sharma | CRM | 0.95 |
| email | priya.sharma@meridian.com | CRM | 0.99 |
| phone | +971501234567 | ECOMM (normalised) | 0.97 |
| city | Dubai | CRM/ECOMM | 1.0 |
| country | UAE | CRM | 0.98 |
| loyalty_tier | Gold | LOYALTY | 1.0 |

## CLI Demo Command
```bash
python -m runtimes.cli unearth customer shared/sample_data/output/customers_dirty.csv
python -m runtimes.cli demo
```

## Related Use Cases
- [UC-C02](UC-C02_cross_channel_merge.md) — Cross-channel merge with conflicting loyalty tiers
- [UC-C04](UC-C04_golden_record_conflict.md) — Golden record conflict when sources disagree on key fields
