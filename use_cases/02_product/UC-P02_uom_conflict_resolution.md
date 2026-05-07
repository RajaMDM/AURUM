# UC-P02: UOM Conflict Resolution

## Summary
The same product is measured in EA (each) in ERP, KG in the warehouse WMS, and "Pc" in the ECOMM catalogue. When an order for 5 units arrives, the fulfilment system doesn't know if that means 5 pieces or 5 kilograms. A single UOM conflict can cause over-shipment, billing errors, and customer disputes. AURUM's product profiler detects UOM heterogeneity and flags it for survivorship resolution.

## Domain
Product

## AURUM Stage(s)
UNEARTH · REFINE · UNFURL

## Business Impact
- Over/under fulfilment — 5 KG shipped instead of 5 pieces
- Invoicing errors — price per KG ≠ price per piece
- Warehouse pick errors — pickers follow WMS UOM, not ERP
- If product is a food item, wrong UOM creates regulatory labelling violations

## Scenario Setup
"Coffee Blend A" is sold by the piece (retail bag) in the ECOMM store and by weight (KG) in the B2B wholesale channel. The ERP models it as EA. The WMS, set up for the B2B channel, uses KG. ECOMM uses "Pc". These are DIFFERENT valid UOMs for the same product — the resolution isn't to pick one, but to establish the canonical UOM per channel and conversion factor.

## Example Records

| field | PIM-00091 | ERP-00091 | WMS-00091 | ECOMM-00091 |
|-------|-----------|-----------|-----------|-------------|
| sku | SKU-0091 | SKU-0091 | SKU-0091 | SKU-0091 |
| name | Coffee Blend A | Coffee Blend A | coffee blend a | COFFEE BLEND A |
| uom | EA | EA | KG | Pc |
| price | 35.00 | 35.00 | 280.00 | 35.00 |

## AURUM Pipeline Walk-Through

**ASSAY** — All four records map to canonical schema. UOM field has 3 distinct values across 4 sources.

**UNEARTH** — Product profiler UOM whitelist rule fires: `Pc` is not in the approved whitelist `[EA, Each, KG, kg, Pc, PCS]` — actually Pc IS in the extended whitelist but flagged for normalisation. Cross-record UOM inconsistency flagged as a WARNING (not an error) because KG may be intentional for WMS.

**REFINE** — Cluster formed (SKU exact match). Survivorship: PIM/ERP/ECOMM all agree on EA/Pc (retail UOM). WMS KG retained as `alt_uom` with `conversion_factor: 8` (1 bag = 8 KG — must be configured by steward). Golden UOM = EA (primary, PIM trust).

**UNFURL** — Golden record includes both `uom: EA` and `alt_uom: KG` with `uom_conversion: 8` so both retail and wholesale channels get what they need.

## Stewardship Decision Point
The steward must confirm the KG conversion factor (how many KG per EA). AURUM flags this as a required steward input — it cannot be derived from the data alone. Without the conversion, the WMS UOM conflict is unresolvable automatically.

## Expected Golden Record

| field | golden_value | source | confidence |
|-------|-------------|--------|------------|
| uom | EA | PIM | 0.98 |
| alt_uom | KG | WMS | 0.95 |
| uom_conversion | [steward input required] | — | — |
| price | 35.00 | PIM/ERP/ECOMM | 1.0 |

## CLI Demo Command
```bash
python -m runtimes.cli unearth product shared/sample_data/output/products_dirty.csv
```

## Related Use Cases
- [UC-P01](UC-P01_sku_deduplication.md) — SKU deduplication before UOM resolution
- [UC-P05](UC-P05_cross_system_price_conflict.md) — Price conflict (often co-occurs with UOM conflicts)
