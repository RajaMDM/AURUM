# UC-XD03: Vendor × Product — Sourcing Conflict

## Domains
Vendor · Product

## Summary
Product `SKU-0077` (Wireless Headphones) is sourced from three vendors according to the ERP. After vendor MDM runs, two of those three vendors were merged into one golden vendor record — the product's `approved_vendor_list` now has a duplicate entry. Simultaneously, the product's golden record (post-dedup) has a different SKU than what the vendor's own catalogue uses — creating a sourcing mismatch that causes purchase orders to reference wrong SKUs to the vendor.

## Business Impact
- Purchase orders raised with wrong vendor SKU reference → vendor can't process → supply chain delay
- Approved Vendor List (AVL) has ghost duplicate entries — procurement policy requires three independent vendors, but two are actually one → single-source risk undetected
- Product compliance: some products require vendor certification — duplicate vendor entries may show two certifications that are actually one
- Spend analytics: total spend with the consolidated vendor is split — volume discount thresholds missed

## Scenario Setup

**Before MDM:**
- Product `SKU-0042` approved vendors: `VEND-00101` (AlBaraka Electronics), `VEND-00102` (Al Baraka Electronics LLC), `VEND-00301` (TechSource ME)
- `VEND-00101` and `VEND-00102` were duplicates → merged by Vendor MDM into `GLD-VEND-00101`
- Product uses vendor's internal part number `VPN-HDP-442` — vendor golden record now uses `VPN-HDP-442-REV2`

**After MDM:**
- Approved vendors list has `GLD-VEND-00101` twice (from old entries) and `GLD-VEND-00301` once
- Product catalogue cross-reference table still has old vendor part number

## Example Records

| product_golden_id | vendor_source_id | vendor_golden_id | vendor_part_no | status |
|------------------|----------------|-----------------|---------------|--------|
| GLD-PROD-00042 | VEND-00101 | GLD-VEND-00101 | VPN-HDP-442 | Stale ref |
| GLD-PROD-00042 | VEND-00102 | GLD-VEND-00101 | VPN-HDP-442 | Duplicate |
| GLD-PROD-00042 | VEND-00301 | GLD-VEND-00301 | VPN-HDP-X91 | Valid |

## AURUM Pipeline Walk-Through

**Cross-Domain UNEARTH** — After Vendor MDM completes, Product domain cross-reference check:
- Scan all product-vendor relationships
- Detect: `GLD-VEND-00101` appears twice in the AVL for `GLD-PROD-00042` → `AVL_DUPLICATE` flagged
- Vendor part number: `VPN-HDP-442` → vendor golden record now lists `VPN-HDP-442-REV2` → `PART_NUMBER_STALE` flagged

**Cross-Domain REFINE** — AVL deduplicated: one entry for `GLD-VEND-00101`. Part number updated to `VPN-HDP-442-REV2` (from vendor golden record). Single-source risk warning raised (only 2 distinct vendors now instead of 3).

**UNFURL** — Updated product-vendor relationships published. Procurement receives: single-source risk alert for this SKU. ERP purchase order template updated with new vendor part number.

**MARK** — `CROSS_DOMAIN_AVL_DEDUPLICATED(GLD-PROD-00042: 3→2 vendors, GLD-VEND-00101 deduplicated)` logged. Procurement Director notified of single-source risk.

## Stewardship Decision Point
Procurement Manager (Amara) reviews the single-source risk. Initiates a new vendor qualification process to find a third independent source for this product. In the interim, safety stock increased.

## CLI Demo Command
```bash
python -m runtimes.cli demo
```

## Related Use Cases
- [UC-V04](../03_vendor/UC-V04_duplicate_vendor_detection.md) — Vendor dedup that triggered this cross-domain issue
- [UC-P05](../02_product/UC-P05_cross_system_price_conflict.md) — Price conflict with the same vendor
