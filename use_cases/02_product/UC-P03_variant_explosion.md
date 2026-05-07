# UC-P03: Variant Explosion — Colour and Size as Separate Records

## Summary
A running shoe product exists in ERP as a single SKU with size/colour as attributes. When ECOMM imported the catalogue, it exploded each size-colour combination into a separate product record — creating 18 records where one parent should exist. These 18 records now clutter the PIM, inflate product counts, and make hierarchy-aware reporting impossible. AURUM identifies the variant pattern and groups them under a single parent golden record with variants.

## Domain
Product

## AURUM Stage(s)
ASSAY · REFINE · UNFURL

## Business Impact
- Category management reporting shows 18 SKUs instead of 1 — product count KPI is wrong
- Promotions applied at product level must be replicated 18 times — error-prone
- Search ranking diluted across 18 near-identical ECOMM listings
- Inventory roll-up to parent SKU is impossible without variant hierarchy

## Scenario Setup
"Running Shoes Model X" comes in 3 sizes (38, 40, 42) and 3 colours (Black, White, Red) = 9 variants. ECOMM created one record per variant. The ERP has them as a single SKU `SKU-0055` with size/colour as ERP attributes. The PIM has the parent product only.

## Example Records

| sku | name | source | size | colour |
|-----|------|--------|------|--------|
| SKU-0055 | Running Shoes Model X | ERP | — | — |
| ECOMM-RSX-38-BLK | Running Shoes Model X Black 38 | ECOMM | 38 | Black |
| ECOMM-RSX-38-WHT | Running Shoes Model X White 38 | ECOMM | 38 | White |
| ECOMM-RSX-40-BLK | Running Shoes Model X Black 40 | ECOMM | 40 | Black |
| ... | ... | ... | ... | ... |

## AURUM Pipeline Walk-Through

**ASSAY** — Schema inspector detects `size` and `colour` fields in ECOMM but not ERP/PIM. Notes high name similarity across 9 ECOMM records.

**UNEARTH** — Profiler flags: 9 records with near-identical names, same brand, same category — anomaly score HIGH. Pattern detected: name suffix follows `[Product] [Colour] [Size]` template.

**REFINE** — Matcher clusters the 9 ECOMM records as variants of the ERP parent. Survivorship creates a parent golden record `GLD-PROD-0055` and 9 child variant records with parent_id link.

**UNFURL** — Published as hierarchy: parent + 9 variants. Category management gets parent rollup. ECOMM gets its variant-level records with `parent_golden_id` set.

## Stewardship Decision Point
Steward confirms the variant grouping logic — AURUM proposes the cluster, steward approves. If the steward disagrees with any variant assignment, they can split it out.

## Expected Golden Record
Parent `GLD-PROD-0055`: `name: Running Shoes Model X`, `variant_count: 9`, `has_variants: true`.
Each child: `parent_id: GLD-PROD-0055`, `size: 38`, `colour: Black`, etc.

## CLI Demo Command
```bash
python -m runtimes.cli unearth product shared/sample_data/output/products_dirty.csv
```

## Related Use Cases
- [UC-P01](UC-P01_sku_deduplication.md) — Basic SKU deduplication without variants
