# UC-GS01: New Store Opening — All 7 Domains in One Event

## Domains
**Customer · Product · Vendor · Asset · Location · Employee · Counterparty**

## Summary

A retail company is opening a new store — **Dubai Hills Mall, Store 2A** — on the 1st of January. This is a single business event. But in the data world, it is a **7-domain cascade**: a new Location must be mastered, a new Employee roster must be onboarded, Assets must be provisioned and linked to the location, Products must be listed with the correct UOM and pricing, Vendors must be qualified to supply the store, the landlord becomes a Counterparty, and the loyalty Customers from the surrounding catchment area must be re-assigned to the new store in the CRM.

AURUM must master all 7 domains — in the right sequence, with the right dependencies — before the doors open on Day 1. Every domain has its own DQ issues. Every domain links to every other. If any one domain fails, the store opening is delayed or opens with broken systems.

---

## Business Impact

If MDM is not done correctly before Day 1:

| Domain Failure | Consequence |
|----------------|------------|
| Location not mastered | Store doesn't exist in ERP, WMS, CRM — no purchase orders, no delivery routes, no customer facing page |
| Employee not linked | Staff can't log into the POS system (AD account not tied to the store location) |
| Asset not provisioned | POS terminals have no asset record — can't be insured, can't be maintained under SLA |
| Product not listed | Store has no product catalogue — POS has nothing to scan |
| Vendor not qualified | No approved supplier for the store — nothing to stock the shelves |
| Counterparty not onboarded | Landlord lease not in the system — first rent payment fails, legal breach of lease |
| Customer not reassigned | Loyalty customers from the catchment area not associated with the new store — they get promotions for a store 20km away |

---

## The 7-Domain Dependency Chain

```
         [LOCATION]
              │
    ┌─────────┼──────────────────┐
    ▼         ▼                  ▼
[EMPLOYEE] [ASSET]         [COUNTERPARTY]
    │         │              (Landlord)
    │         │
    ▼         ▼
[PRODUCT] [VENDOR]
              │
              ▼
         [CUSTOMER]
     (catchment re-assign)
```

**Sequencing rule:** Location must be mastered FIRST — every other domain references `location_id`. Employee and Asset can run in parallel after Location. Product and Vendor can run in parallel. Customer re-assignment is last (depends on Employee, Product, Location all being clean).

---

## Domain-by-Domain Walkthrough

---

### 1. LOCATION — Master the Store First

**The DQ Issues:**
- Store was registered in WMS before construction was complete — address is the contractor's site office, not the store address
- Lat/lon from the property developer's CAD file is 200m off (parking lot, not the store entrance)
- The mall hierarchy in ERP doesn't have "Dubai Hills Mall" as a location node yet — parent_id is null

**AURUM Actions (ASSAY → UNEARTH → REFINE → MARK):**
- ASSAY: Ingest from ERP (shell record), WMS (wrong address), YEXT (correct address from mall directory)
- UNEARTH: Null Island detector flags wrong lat/lon. Address inconsistency flagged. Null parent_id flagged.
- REFINE: YEXT address wins (most recent, mall-verified). Lat/lon corrected via batch geocoding. Parent node `Dubai Hills Mall (LOC-R-DHM)` created first, then `Store 2A` linked as child.
- UNFURL: `GLD-LOC-STORE-2A` published. All other domains can now reference this golden location_id.
- MARK: `NEW_LOCATION_MASTERED(GLD-LOC-STORE-2A, type=Store, parent=LOC-R-DHM, effective=2025-01-01)`

**Golden Record:**
```
GLD-LOC-STORE-2A
  name: Dubai Hills Mall — Store 2A
  type: Store
  address: Unit 2A, Dubai Hills Mall, Al Hebiah, Dubai
  postal_code: 00000
  lat: 25.1102
  lon: 55.2650
  parent_id: LOC-R-DHM (Dubai Hills Mall)
  timezone: Asia/Dubai
```

---

### 2. EMPLOYEE — Hire the Team, Link to the Store

**The DQ Issues:**
- 22 new staff onboarded — HRMS has them, AD provisioning is 4 days delayed
- Store Manager (Inaayah) exists in the company as a Tech Writer (different role) — HRMS has two records, one active for old role, one pending for new role
- 3 seasonal staff are rehires from last year's Ramadan pop-up — rehire detection needed
- `location_id` on all 22 employee records is still the contractor's site office address (LOC-OLD-SITE), not `GLD-LOC-STORE-2A`

**AURUM Actions:**
- UNEARTH: Inactive manager link (4 AD accounts not yet provisioned — flagged). Inaayah's dual record → ROLE_TRANSITION pattern, not duplicate. 3 rehires detected via email match on inactive records.
- REFINE: Inaayah's old record linked as predecessor, new role record becomes golden. Rehires linked as LIFECYCLE_CHAIN. Location updated: LOC-OLD-SITE → GLD-LOC-STORE-2A for all 22.
- UNFURL: AD provisioning request generated for 4 pending accounts. POS system receives employee-location assignments. Floor warden list generated with correct store location.
- MARK: `EMPLOYEE_STORE_ASSIGNMENT(22 employees → GLD-LOC-STORE-2A, effective=2025-01-01, 3 rehires detected)`

---

### 3. ASSET — Provision and Tag the Equipment

**The DQ Issues:**
- 35 assets (POS terminals, iPads, HVAC units, server rack) registered in CMDB before delivery — serial numbers are placeholders (`SN-TBD-001` to `SN-TBD-035`)
- Asset tags are pre-printed but not yet scanned — asset_tag field has leading spaces and inconsistent format (`AST-2A-001` vs `ast2a001` vs `AST_2A_001`)
- `location_id` on all assets references the WMS staging warehouse (`LOC-WH-STAGING`), not the store — needs updating on Day 1 when assets are physically moved

**AURUM Actions:**
- ASSAY: Asset tag normalisation → all to `AST-2A-NNN`. Serial number placeholders flagged for replacement on delivery.
- UNEARTH: `SN-TBD-*` flagged as placeholders, HIGH severity. Location mismatch flagged.
- REFINE: Placeholder serials held in `PENDING_DELIVERY` state. On Day 1, actual serial numbers scanned at delivery → matched to placeholder records by asset tag → placeholders replaced with real serials.
- UNFURL: Asset golden records published with `location_id: GLD-LOC-STORE-2A` (updated on physical move). Insurance certificate generated from the asset register.
- MARK: `ASSET_PROVISIONED(35 assets → GLD-LOC-STORE-2A, serial_numbers_confirmed=35, effective=2025-01-01)`

**Asset-Employee links established:**
- POS terminal 1 → assigned_to: Store Manager (GLD-EMP-INAAYAH)
- HVAC units → assigned_to: Facilities team cost centre
- Server rack → assigned_to: IT Infra (GLD-EMP-IT-INFRA)

---

### 4. PRODUCT — Stock the Shelves

**The DQ Issues:**
- Store 2A carries 340 SKUs. 28 are UAE exclusives not in the ECOMM catalogue (different barcodes, AED pricing only)
- 12 SKUs have UOM conflicts (same issue as UC-P02) — WMS uses KG, POS needs EA
- 5 products were discontinued last month but still appear in the store's import list

**AURUM Actions:**
- UNEARTH: 28 store-exclusive products — barcode DQ check, UAE-specific price validation. 12 UOM conflicts flagged. 5 discontinued products flagged (`status: Inactive`).
- REFINE: UOM conflicts resolved (EA as primary, KG as alt with conversion). Discontinued products excluded from store catalogue.
- UNFURL: Product golden records linked to `GLD-LOC-STORE-2A` via product-location availability table. POS system receives 335 approved SKUs (340 minus 5 discontinued). WMS receives stock transfer list with correct UOMs.
- MARK: `PRODUCT_STORE_LISTING(335 SKUs → GLD-LOC-STORE-2A, 5 excluded=discontinued, 12 UOM conflicts resolved)`

---

### 5. VENDOR — Qualify the Suppliers

**The DQ Issues:**
- 8 vendors supply this store. 3 are already qualified in the system. 5 are new — 2 have incomplete TRNs, 1 has a name mismatch between the trade licence and the ERP record
- One vendor (`Al Baraka Supplies`) was also found in the Customer master (they buy corporate gifts) — dual-role detected

**AURUM Actions:**
- UNEARTH: 2 incomplete TRNs flagged (UC-V03 pattern). Name mismatch: trade licence vs ERP → legal name from trade licence wins.
- REFINE: Al Baraka → dual-role link to customer record (UC-V05 pattern). 5 new vendors onboarded with DQ remediation workflow initiated for the 2 with TRN issues.
- UNFURL: 6 fully qualified vendors linked to `GLD-LOC-STORE-2A` via store-vendor supply list. 2 vendors in `PENDING_TRN` status — provisional supply approved for 30 days pending remediation.
- MARK: `VENDOR_STORE_QUALIFICATION(8 vendors → GLD-LOC-STORE-2A, 6 approved, 2 provisional, 1 dual-role detected)`

---

### 6. COUNTERPARTY — Onboard the Landlord

**The DQ Issues:**
- The landlord is Emaar Properties PJSC. Legal has one record in the contract system. Treasury has a different record with a different LEI (legacy placeholder). Finance has no record — they've been booking lease payments to a manual GL entry.
- LEI on Treasury record fails check-digit validation (UC-CP02 pattern)

**AURUM Actions:**
- UNEARTH: LEI validation failure on Treasury record. Three source records for the same legal entity.
- REFINE: Three records merged into one golden counterparty `GLD-CP-EMAAR`. Correct LEI sourced from GLEIF registry. Lease contract linked to the counterparty golden record.
- UNFURL: Emaar golden record published. Finance GL manual entry replaced with a proper counterparty-coded payable. IFRS 16 right-of-use asset registered against `GLD-LOC-STORE-2A` with Emaar as lessor.
- MARK: `COUNTERPARTY_ONBOARDED(GLD-CP-EMAAR, role=Landlord, linked_location=GLD-LOC-STORE-2A, lease_start=2025-01-01)`

---

### 7. CUSTOMER — Assign the Catchment Area

**The DQ Issues:**
- The CRM's loyalty system uses a `preferred_store` field to route offers. 4,200 customers in the Dubai Hills catchment area currently have `preferred_store: Dubai Mall` (the nearest previous store). After the new store opens, these should be offered the option to switch — but 1,100 of them have been through identity resolution (UC-C01) and now have a golden_id that doesn't match what the loyalty system has on file.
- 340 customers have no `preferred_store` set — null field, never assigned.

**AURUM Actions:**
- UNEARTH: 1,100 loyalty records with stale source_id (pre-merge) flagged. 340 null `preferred_store` records flagged for first-time assignment.
- REFINE: Source ID resolution table applied — all 4,200 catchment customers confirmed as valid golden records. `preferred_store` field updated to offer `GLD-LOC-STORE-2A` as an option (not forced — customer choice respected for GDPR/PDPL compliance).
- UNFURL: CRM receives updated customer list segmented by catchment. Marketing campaign triggered: "New store near you — Dubai Hills Mall. Switch your preferred store for exclusive opening offers." 4,200 customers, 340 first-time store assignments.
- MARK: `CUSTOMER_CATCHMENT_ASSIGNED(4200 customers, GLD-LOC-STORE-2A catchment, 1100 golden_ids re-anchored, 340 first-assigned)`

---

## The Complete Golden Web on Day 1

```
GLD-LOC-STORE-2A (Dubai Hills Mall — Store 2A)
├── employees: 22 × GLD-EMP-* (all linked, AD provisioned)
├── assets: 35 × GLD-ASSET-* (serial numbers confirmed, insured)
├── products: 335 × GLD-PROD-* (POS loaded, WMS stocked)
├── vendors: 6 approved + 2 provisional × GLD-VEND-*
├── counterparty: GLD-CP-EMAAR (landlord, lease live, IFRS 16 booked)
└── customers: 4,200 × GLD-CUST-* (catchment assigned, campaign sent)
```

Every domain. Every golden record. Every cross-domain link. All consistent. All auditable. All in MARK's lineage store.

---

## The Stewardship Team on Day 1

| Domain | Steward | Action |
|--------|---------|--------|
| Location | Pierre (EA Head) | Confirmed hierarchy, approved parent node |
| Employee | Jin (Stewardship) | Confirmed rehires, approved role transition |
| Asset | Carlos (DataOps) | Confirmed serial numbers on delivery |
| Product | Arun (BI Head) | Approved store catalogue, excluded discontinued |
| Vendor | Amara (BA) | Confirmed qualifications, noted single-source risk |
| Counterparty | Nadia (Governance) + Tariq (Security) | Confirmed Emaar LEI, screening CLEAR |
| Customer | Shazia (DQ Lead) | Confirmed catchment mapping, PDPL-compliant opt-in |

---

## AURUM Lineage Summary for the New Store Opening

```
MARK query: GET /lineage?location_id=GLD-LOC-STORE-2A
→ location_mastered: 2024-12-01
→ employees_assigned: 22 (2024-12-15)
→ assets_provisioned: 35 (2024-12-28, serial confirmed 2025-01-01)
→ products_listed: 335 (2024-12-20)
→ vendors_qualified: 8 (2024-12-10)
→ counterparty_onboarded: Emaar (2024-12-05)
→ customers_assigned: 4200 (2025-01-01)
→ store_ready: TRUE
→ day_1_blockers: 0
```

---

## CLI Demo Command
```bash
python shared/sample_data/generate_all.py   # generate all 7 domain datasets
python demo/end_to_end_demo.py              # run full pipeline
python -m runtimes.cli demo                 # CLI version
```

---

## Related Use Cases (all of them)
This scenario references and builds on every single-domain and cross-domain use case in the library. It is the capstone.

| Domain | Key Single-Domain UCs |
|--------|----------------------|
| Customer | UC-C01, UC-C03 |
| Product | UC-P01, UC-P02, UC-P04 |
| Vendor | UC-V01, UC-V03, UC-V05 |
| Asset | UC-A02, UC-A04 |
| Location | UC-L02, UC-L04, UC-L05 |
| Employee | UC-E01, UC-E04 |
| Counterparty | UC-CP02, UC-CP03 |
| Cross-Domain | UC-XD01, UC-XD02, UC-XD03, UC-XD04, UC-XD05 |
