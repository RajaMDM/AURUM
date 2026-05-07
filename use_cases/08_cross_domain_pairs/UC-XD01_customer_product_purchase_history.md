# UC-XD01: Customer × Product — Purchase History Integrity

## Domains
Customer · Product

## Summary
The CRM stores purchase history as `customer_id + product_sku`. After MDM runs:
- 3 customer records were merged into 1 golden record (new golden_id)
- 8 product SKU records were deduplicated into 4 golden SKUs

Now all historical purchase records reference old source IDs that no longer exist as standalone records. Analytics, CLV calculation, and product affinity models all break unless purchase history is re-anchored to the golden IDs. This is the hidden cost of MDM that teams forget to plan for — referential integrity across domains post-mastering.

## Business Impact
- Customer lifetime value (CLV) is wrong — purchases split across 3 pre-merge IDs are only partially counted
- Product affinity model ("customers who bought X also bought Y") uses wrong product IDs — recommendations break
- Warranty and returns processing references old customer/product IDs that no longer match the golden record
- GDPR right to erasure: deleting a customer golden record must cascade to purchase history — broken links mean data lingers

## Scenario Setup
Before MDM: customer `CRM-00101`, `ECOMM-00234`, `LOYALTY-00089` — all Priya Sharma. Product `SKU-0042`, `sku_0042`, `SKU0042`, `" SKU-0042"` — all the same headphones.

Purchase history table has 47 rows referencing these old IDs in various combinations. After MDM: `GLD-CUST-00101` and `GLD-PROD-00042` are the authoritative IDs.

## Example Records (purchase history before MDM)

| purchase_id | customer_id | sku | qty | date |
|------------|------------|-----|-----|------|
| PO-10001 | CRM-00101 | SKU-0042 | 1 | 2024-01-15 |
| PO-10002 | ECOMM-00234 | SKU0042 | 2 | 2024-03-20 |
| PO-10003 | LOYALTY-00089 | sku_0042 | 1 | 2024-06-10 |

## AURUM Pipeline Walk-Through

**Customer REFINE** — `CRM-00101`, `ECOMM-00234`, `LOYALTY-00089` → `GLD-CUST-00101`. Source ID map maintained.

**Product REFINE** — `SKU-0042`, `sku_0042`, `SKU0042`, `" SKU-0042"` → `GLD-PROD-00042`. Source ID map maintained.

**Cross-Domain UNFURL** — AURUM publishes a **source ID resolution table**: every old source ID maps to its golden_id. Downstream systems (CRM analytics, recommendation engine) consume this table to re-anchor their foreign keys.

**MARK** — `CROSS_DOMAIN_REANCHOR(purchase_history: 47 rows updated, customer_ids→golden, sku→golden)` logged.

## Resolution

| purchase_id | old_customer_id | golden_customer_id | old_sku | golden_sku |
|------------|----------------|-------------------|---------|-----------|
| PO-10001 | CRM-00101 | GLD-CUST-00101 | SKU-0042 | GLD-PROD-00042 |
| PO-10002 | ECOMM-00234 | GLD-CUST-00101 | SKU0042 | GLD-PROD-00042 |
| PO-10003 | LOYALTY-00089 | GLD-CUST-00101 | sku_0042 | GLD-PROD-00042 |

All three purchases now correctly attributed to one customer buying one product — total: 4 units. CLV is now accurate.

## Stewardship Decision Point
Arun (BI Head) validates the re-anchored purchase history before it feeds the CLV model. Confirms: 47 rows updated, zero orphaned purchase records. Recommendation engine retrained on corrected data.

## CLI Demo Command
```bash
python -m runtimes.cli demo
```

## Related Use Cases
- [UC-C01](../01_customer/UC-C01_identity_resolution.md) — Customer identity resolution (prerequisite)
- [UC-P01](../02_product/UC-P01_sku_deduplication.md) — Product SKU dedup (prerequisite)
- [UC-GS01](../09_grand_scenario/UC-GS01_new_store_opening.md) — Grand scenario where all domain cross-references must be maintained
