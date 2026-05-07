# Product Domain — Use Cases

The **Product domain** mastering challenge centres on variant explosion, SKU format heterogeneity, and UOM conflicts. A single product may be represented with dozens of SKU formats across PIM, ERP, ECOMM, and WMS — with conflicting prices, units, and barcodes. AURUM's product profiler and matcher normalise these into a clean, trusted golden product record.

## Use Cases

| Code | Title | Complexity | Key Stages |
|------|-------|-----------|------------|
| [UC-P01](UC-P01_sku_deduplication.md) | SKU Deduplication Across Systems | Medium | ASSAY, REFINE, UNFURL |
| [UC-P02](UC-P02_uom_conflict_resolution.md) | UOM Conflict Resolution | Low | UNEARTH, REFINE |
| [UC-P03](UC-P03_variant_explosion.md) | Variant Explosion — Colour/Size as Separate Records | High | REFINE, UNFURL |
| [UC-P04](UC-P04_barcode_dq_failure.md) | Barcode DQ Failure — Invalid EAN/UPC | Low | ASSAY, UNEARTH |
| [UC-P05](UC-P05_cross_system_price_conflict.md) | Cross-System Price Conflict | Medium | REFINE, UNFURL, MARK |
