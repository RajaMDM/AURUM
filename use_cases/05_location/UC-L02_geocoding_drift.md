# UC-L02: Geocoding Drift — Null Island Detection

## Summary
Eight location records have lat/lon coordinates of `0.0, 0.0` — the infamous "Null Island" in the Gulf of Guinea, 600km off the coast of Africa. These are default null values that were never populated. Another 12 records have coordinates that are geographically inconsistent with their stated city (e.g., lat/lon pointing to London while city = Dubai). AURUM's location profiler catches both and flags them before they corrupt map-based analytics.

## Domain
Location

## AURUM Stage(s)
UNEARTH

## Business Impact
- Store finder / locator app shows stores in the ocean — customer-facing embarrassment
- Delivery routing systems use lat/lon for route optimisation — wrong coordinates = wrong routes
- Geo-analytics (heat maps, catchment areas, drive-time analysis) completely invalid
- Emergency services integration: if a store has an incident, wrong coordinates sent to responders

## Scenario Setup
Legacy locations were migrated from a flat-file system that used `0` as the null sentinel for lat/lon. Some records were geocoded from a batch geocoding service that had a bug — it returned coordinates for the city centre of London instead of Dubai for records where the country code was ambiguous (`AE` was misread as a UK postcode area).

## Example Records

| location_code | name | city | country | lat | lon | issue |
|--------------|------|------|---------|-----|-----|-------|
| LOC-011 | Abu Dhabi HQ | Abu Dhabi | UAE | 0.0 | 0.0 | Null Island |
| LOC-012 | Dubai Marina Store | Dubai | UAE | 51.5074 | -0.1278 | London coords |
| LOC-013 | Sharjah Warehouse | Sharjah | UAE | 25.3462 | 55.4209 | Correct ✓ |
| LOC-014 | Ajman Office | Ajman | UAE | 0.0 | 0.0 | Null Island |

## AURUM Pipeline Walk-Through

**ASSAY** — Schema inspector: `lat` and `lon` have value `0.0` on 8 records. Flagged as possible null sentinel values.

**UNEARTH** — Location profiler geocoding rules:
- `null_island_detector`: `lat == 0.0 AND lon == 0.0` → 8 records flagged `NULL_ISLAND`
- `lat_lon_range_uae`: for country=UAE, lat must be in `[22.0, 26.5]`, lon in `[51.0, 56.5]` → 12 records fail (London coords: lat 51, lon -0.1)
- `lat_lon_city_consistency`: geocode city name independently, compare to stored lat/lon → 12 mismatches flagged

**REFINE** — Location records with bad coordinates: coordinates excluded from matching. Name + type + city used for matching. Published with `geocode_status: INVALID`.

## Stewardship Decision Point
Carlos (DataOps) runs a batch re-geocoding job against a reliable geocoding API using the address fields. Results reviewed by Lena (Integration). 19 of 20 records auto-corrected. 1 record (LOC-019) has insufficient address data — manually geocoded using Google Maps.

## Expected Golden Record
After remediation: `lat: 25.1972`, `lon: 55.2796` (Dubai Marina), `geocode_status: VERIFIED`, `geocode_source: BATCH_RECODE_2024-11`.

## CLI Demo Command
```bash
python -m runtimes.cli unearth location shared/sample_data/output/locations_dirty.csv
```

## Related Use Cases
- [UC-L04](UC-L04_address_standardisation.md) — Address standardisation feeds geocoding
