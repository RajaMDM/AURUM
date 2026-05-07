# UC-P01: SKU Deduplication Across Systems

## Summary
A wireless headphone product exists in PIM as `SKU-0042`, in ERP as `sku_0042`, in ECOMM as `SKU0042`, and in WMS with a leading space ` SKU-0042`. These four records are the same physical product but treated as four different SKUs across the supply chain. The result: split inventory, fragmented order history, and broken reorder logic. AURUM normalises and deduplicates these into one authoritative golden product record.

## Domain
Product

## AURUM Stage(s)
ASSAY · UNEARTH · REFINE · UNFURL

## Business Impact
- Inventory counts split across 4 phantom SKUs — stock levels appear lower than reality, triggering unnecessary purchase orders
- Sales reports show the same product in four rows — revenue appears fragmented
- ECOMM and WMS can't reconcile orders — fulfilment failures
- Promotional pricing applied to only one SKU variant — others sold at wrong price

## Scenario Setup
The product "Wireless Headphones Pro" was first created in PIM (the master system of intent) as SKU-0042. During ERP migration, a script lowercased all SKUs. The ECOMM platform strips hyphens. WMS imported from a CSV with a leading space. No system enforced a canonical format at write time.

## Example Records

| field | PIM-00042 | ERP-00042 | ECOMM-00042 | WMS-00042 |
|-------|-----------|-----------|-------------|-----------|
| sku | SKU-0042 | sku_0042 | SKU0042 | " SKU-0042" |
| name | Wireless Headphones Pro | wireless headphones pro | WIRELESS HEADPHONES PRO | Wireless Headphones Pro |
| uom | EA | Each | Pc | EA |
| barcode | 6901234567890 | 6901234567890 | | 6901234567890 |
| price | 299.00 | 299.00 | 299.00 | |

## AURUM Pipeline Walk-Through

**ASSAY** — Schema inspector detects SKU format variation across sources. Flags leading whitespace on WMS record. Maps all to canonical `sku` field.

**UNEARTH** — Product profiler SKU normalisation rule: strips whitespace, lowercases, removes separators → all four normalise to `sku0042`. Profiler flags UOM inconsistency (EA/Each/Pc). Missing barcode on ECOMM flagged.

**REFINE** — Post-normalisation, all four SKUs match exactly. Cluster formed. Survivorship: PIM is highest-trust source for product attributes. `name: Wireless Headphones Pro` (PIM casing), `uom: EA` (PIM), `barcode: 6901234567890` (PIM/ERP/WMS consensus).

**UNFURL** — Golden product published as `GLD-PROD-00042` with canonical `sku: SKU-0042`.

## Stewardship Decision Point
No steward intervention needed for this scenario — the match is deterministic after normalisation. AURUM auto-resolves and logs. Steward may review the UOM rationalisation (EA vs Each vs Pc) if they have downstream systems with strict UOM contracts.

## Expected Golden Record

| field | golden_value | source | confidence |
|-------|-------------|--------|------------|
| sku | SKU-0042 | PIM | 1.0 |
| name | Wireless Headphones Pro | PIM | 0.99 |
| uom | EA | PIM | 0.95 |
| barcode | 6901234567890 | PIM/ERP/WMS consensus | 1.0 |
| price | 299.00 | PIM/ECOMM/ERP consensus | 1.0 |

## CLI Demo Command
```bash
python -m runtimes.cli unearth product shared/sample_data/output/products_dirty.csv
```

## Related Use Cases
- [UC-P02](UC-P02_uom_conflict_resolution.md) — UOM conflict after SKU consolidation
- [UC-P04](UC-P04_barcode_dq_failure.md) — Barcode DQ failure on the same product set
