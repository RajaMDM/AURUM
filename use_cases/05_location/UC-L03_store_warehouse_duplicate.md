# UC-L03: Store vs Warehouse Duplicate

## Summary
"Dubai Investment Park" appears twice in the location master — once as a Store (LOC-045, entered by the retail team) and once as a Warehouse (LOC-089, entered by the logistics team). They are the same physical building, with the ground floor operating as a retail showroom and the upper floors as a stock holding area. Without MDM recognising this as one location with dual functions, stock movements, rent apportionment, and headcount allocation are all anchored to the wrong records.

## Domain
Location

## AURUM Stage(s)
REFINE · UNFURL

## Business Impact
- Rent apportioned twice to two location codes — double the cost booked in finance
- Headcount split: retail staff under LOC-045, warehouse staff under LOC-089 — total headcount for this site is invisible
- Stock movements between "store" and "warehouse" are recorded as inter-location transfers — generating phantom logistics costs
- Lease management: two lease records for one physical property — IFRS 16 right-of-use asset overstated

## Scenario Setup
The building at Dubai Investment Park has one postal address and one commercial licence. Retail ops created a store location record. Logistics created a warehouse location independently. Both used slightly different names, both reference the same postal code and coordinates.

## Example Records

| field | LOC-045 | LOC-089 |
|-------|---------|---------|
| location_code | LOC-045 | LOC-089 |
| name | Dubai Investment Park Store | DIP Warehouse |
| type | Store | Warehouse |
| address_line1 | Plot 598, DIP Phase 2 | Plot 598 DIP Ph2 |
| city | Dubai | Dubai |
| postal_code | 1234 | 1234 |
| lat | 24.9897 | 24.9897 |
| lon | 55.1745 | 55.1746 |
| parent_id | LOC-R02 | LOC-W01 |

## AURUM Pipeline Walk-Through

**ASSAY** — Both records ingest. Postal code and coordinates are near-identical.

**UNEARTH** — Location profiler: same postal code, lat/lon within 10m → `NEAR_DUPLICATE_CANDIDATE` flagged. Name similarity: `Dubai Investment Park Store` vs `DIP Warehouse` = 0.62 (low — but address signals override).

**REFINE** — Address + postal code + coordinate match → cluster formed despite low name similarity. Survivorship: these are NOT identical — `type` differs meaningfully (Store vs Warehouse). Resolution: single golden location with `type: [Store, Warehouse]` (multi-type) and `sub_locations: [retail_floor, warehouse_floor]`.

**UNFURL** — `GLD-LOC-0045` published: `name: Dubai Investment Park`, `type: Mixed-Use`, `sub_types: [Store, Warehouse]`, both original location codes retained as aliases.

## Stewardship Decision Point
Pierre (EA) and Arun (BI) jointly define the multi-type model. Finance is updated: single lease record, rent split by floor area ratio (60% retail / 40% warehouse) — configured as a finance attribute, not an MDM change.

## Expected Golden Record

| field | golden_value | source |
|-------|-------------|--------|
| name | Dubai Investment Park | Steward-defined |
| type | Mixed-Use | Steward-defined |
| postal_code | 1234 | Consensus |
| lat | 24.9897 | Consensus |

## CLI Demo Command
```bash
python -m runtimes.cli unearth location shared/sample_data/output/locations_dirty.csv
```

## Related Use Cases
- [UC-L05](UC-L05_parent_child_resolution.md) — Parent-child resolution when the merged location has two parent hierarchies
