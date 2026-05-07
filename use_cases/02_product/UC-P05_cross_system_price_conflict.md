# UC-P05: Cross-System Price Conflict

## Summary
A product's price in ERP is AED 299, in ECOMM it's AED 279 (a promotional price that was never reverted), and in the MARKETPLACE it's AED 319 (a partner-set price). Three prices for the same product in live systems. Without MDM resolving which is authoritative, every order channel charges a different price — causing customer complaints, margin erosion, and audit failures.

## Domain
Product

## AURUM Stage(s)
REFINE · UNFURL · MARK

## Business Impact
- Revenue leakage if ECOMM promotional price becomes permanent without approval
- Customer complaints when ECOMM price differs from in-store (ERP-driven) price
- Finance reconciliation fails — three price lines for one product
- Marketplace partner may be in breach of pricing agreement

## Scenario Setup
Product `SKU-0077` (Wireless Headphones) had a Black Friday promotional price of AED 279 applied in ECOMM in November. The promotion ended but the revert script failed — ECOMM still shows 279. ERP has the authoritative RRP of AED 299. The marketplace partner independently set AED 319 (above RRP, which violates the distribution agreement).

## Example Records

| field | ERP-00077 | ECOMM-00077 | MARKETPLACE-00077 |
|-------|-----------|-------------|-------------------|
| sku | SKU-0077 | SKU0077 | SKU-0077 |
| price | 299.00 | 279.00 | 319.00 |
| currency | AED | AED | AED |
| price_type | RRP | Promotional | Partner |
| price_valid_from | 2024-01-01 | 2024-11-29 | 2024-06-01 |
| price_valid_to | | 2024-11-30 | |

## AURUM Pipeline Walk-Through

**ASSAY** — All three records ingest. Schema inspector notes `price` field has 3 distinct values across 3 sources for the same SKU (post-normalisation).

**UNEARTH** — Product profiler: cross-record price variance > 15% threshold → flagged as PRICE_CONFLICT warning. `price_valid_to: 2024-11-30` on ECOMM price has passed — flagged as EXPIRED_PRICE.

**REFINE** — Cluster formed. Survivorship: ERP is configured as system of record for RRP. ECOMM promotional price has expired `price_valid_to` → suppressed. MARKETPLACE price noted as outside RRP band → flagged for commercial team review. Golden price = AED 299.00.

**UNFURL** — Golden record published with `price: 299.00`. ECOMM and MARKETPLACE receive the canonical price via reverse sync. `PRICE_CONFLICT` event logged with all three competing values for audit.

**MARK** — `PRICE_CONFLICT(SKU-0077: ERP=299, ECOMM=279[EXPIRED], MKT=319[ABOVE_RRP], resolved=299)` logged. Commercial team notified of marketplace breach.

## Stewardship Decision Point
Steward reviews the marketplace price (AED 319 above RRP). This may constitute a distribution agreement violation — escalated to the commercial team automatically. Steward approves golden price of 299 and triggers reverse sync to ECOMM and MARKETPLACE.

## Expected Golden Record

| field | golden_value | source | confidence |
|-------|-------------|--------|------------|
| price | 299.00 | ERP | 1.0 |
| currency | AED | ERP | 1.0 |
| price_type | RRP | ERP | 1.0 |

## CLI Demo Command
```bash
python -m runtimes.cli demo
```

## Related Use Cases
- [UC-P02](UC-P02_uom_conflict_resolution.md) — UOM conflict (often paired with price conflicts)
- [UC-V05](../03_vendor/UC-V05_vendor_customer_crossover.md) — Marketplace partner as both vendor and customer
