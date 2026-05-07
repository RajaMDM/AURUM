# UC-C02: Cross-Channel Customer Merge with Conflicting Loyalty Tiers

## Summary
A customer exists in both CRM (Gold tier) and ECOMM (Silver tier) because loyalty tier is managed independently per channel. When AURUM merges the records, the survivorship engine must resolve the conflict using source trust weights — not just pick the most recent value blindly. Getting this wrong means either demoting a loyal customer or inflating tier counts, both with real business consequences.

## Domain
Customer

## AURUM Stage(s)
UNEARTH · REFINE · UNFURL · MARK

## Business Impact
- Incorrectly downgrading a Gold customer to Silver triggers complaints, churn risk, and potential SLA violations
- Inflating tiers by always picking the higher value creates fraudulent loyalty redemptions
- Cross-channel promotions break when tier logic is inconsistent

## Scenario Setup
Mohammed Al-Rashid holds Gold tier in CRM (assigned by a sales rep after a large in-store purchase) and Silver tier in ECOMM (auto-assigned based on online spend alone). Both records are legitimate — the conflict arises because tier logic isn't unified across channels. The correct outcome is Gold, because CRM is the system of record for loyalty tier and the in-store purchase history is authoritative.

## Example Records

| field | CRM-00045 | ECOMM-00312 |
|-------|-----------|-------------|
| first_name | Mohammed | Mohamed |
| last_name | Al-Rashid | Al Rashid |
| email | m.alrashid@meridian.com | m.alrashid@meridian.com |
| phone | +971504567890 | +971504567890 |
| loyalty_tier | Gold | Silver |
| customer_type | VIP | Regular |
| city | Abu Dhabi | Abu Dhabi |

## AURUM Pipeline Walk-Through

**ASSAY** — Both records ingest cleanly. Schema inspector notes `loyalty_tier` and `customer_type` exist in both schemas with different value sets.

**UNEARTH** — Profiler detects `loyalty_tier` value inconsistency across sources for what appears to be the same customer (same email/phone). Flagged as a cross-system conflict, not a DQ failure per se.

**REFINE** — Matcher scores CRM vs ECOMM at 0.96 (email exact match, phone exact match, name near-match). Cluster formed. Survivorship applies source trust weights: CRM trust=0.9, ECOMM trust=0.7 for `loyalty_tier`. CRM's `Gold` wins. `customer_type` resolved to `VIP` by same logic.

**UNFURL** — Golden record published with `loyalty_tier: Gold`, `customer_type: VIP`. Both source IDs retained in `source_ids[]`.

**MARK** — Conflict event logged: `FIELD_CONFLICT(loyalty_tier, CRM=Gold, ECOMM=Silver, resolved=Gold, rule=source_trust)`. Available for steward audit.

## Stewardship Decision Point
AURUM resolves this automatically via source trust weights, but logs the conflict for steward visibility. If the steward has configured ECOMM as higher trust for loyalty (e.g., online spend is the true source), they can override the survivorship rule in the config — no code change required.

## Expected Golden Record

| field | golden_value | source | confidence |
|-------|-------------|--------|------------|
| first_name | Mohammed | CRM | 0.92 |
| last_name | Al-Rashid | CRM | 0.92 |
| email | m.alrashid@meridian.com | CRM/ECOMM | 1.0 |
| phone | +971504567890 | CRM/ECOMM | 1.0 |
| loyalty_tier | Gold | CRM (trust-weighted) | 0.90 |
| customer_type | VIP | CRM (trust-weighted) | 0.90 |

## CLI Demo Command
```bash
python -m runtimes.cli unearth customer shared/sample_data/output/customers_dirty.csv
```

## Related Use Cases
- [UC-C01](UC-C01_identity_resolution.md) — Full identity resolution across 3 source systems
- [UC-C04](UC-C04_golden_record_conflict.md) — Golden record conflict on address fields
