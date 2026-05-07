# AURUM Use-Case Library

> **35 single-domain + 5 cross-domain + 1 grand scenario = 41 real-world MDM playbooks**

This library is the practitioner's companion to the AURUM codebase. Every use case is a realistic enterprise MDM scenario — grounded in actual data problems that data teams face across CRM, ERP, ECOMM, HRMS, Treasury, and Facilities systems.

**Who this is for:**
- **MDM Practitioners** — patterns you'll recognise from your own implementations
- **Data Architects** — cross-domain dependency chains and resolution sequencing
- **Data Stewards** — decision points, escalation patterns, and what to do when AURUM flags something
- **Students & Learners** — end-to-end MDM scenarios with pipeline walk-throughs and expected outcomes
- **Engineers** — CLI commands to run each scenario against the included sample data

---

## Library Structure

```
use_cases/
├── 01_customer/         5 use cases  — Identity, merge, DQ, conflicts, lineage
├── 02_product/          5 use cases  — SKU dedup, UOM, variants, barcode, price
├── 03_vendor/           5 use cases  — Legal entity, hierarchy, tax ID, duplicates, dual-role
├── 04_asset/            5 use cases  — Lifecycle, orphans, drift, serial dedup, lineage
├── 05_location/         5 use cases  — Hierarchy, geocoding, duplicates, address, parent-child
├── 06_employee/         5 use cases  — Identity merge, reorg, multi-role, rehire, cost centre
├── 07_counterparty/     5 use cases  — Dual role, LEI, dedup, jurisdiction, lineage
├── 08_cross_domain_pairs/ 5 use cases — 2-3 domains talking to each other
└── 09_grand_scenario/   1 use case   — All 7 domains in a single business event
```

---

## All 41 Use Cases

### Tier 1 — Single Domain (35 use cases)

#### Customer
| Code | Title | Complexity | Key Stages |
|------|-------|-----------|------------|
| [UC-C01](01_customer/UC-C01_identity_resolution.md) | Identity Resolution Across Source Systems | Medium | ASSAY, UNEARTH, REFINE, UNFURL, MARK |
| [UC-C02](01_customer/UC-C02_cross_channel_merge.md) | Cross-Channel Merge with Conflicting Loyalty Tiers | Medium | UNEARTH, REFINE, UNFURL, MARK |
| [UC-C03](01_customer/UC-C03_dq_email_phone_failure.md) | DQ Failure — Missing Email and Invalid Phone | Low | ASSAY, UNEARTH |
| [UC-C04](01_customer/UC-C04_golden_record_conflict.md) | Golden Record Conflict — Address Field Disagreement | High | REFINE, UNFURL, MARK |
| [UC-C05](01_customer/UC-C05_lineage_audit_trail.md) | Customer Lineage Audit Trail | Medium | MARK, UNFURL |

#### Product
| Code | Title | Complexity | Key Stages |
|------|-------|-----------|------------|
| [UC-P01](02_product/UC-P01_sku_deduplication.md) | SKU Deduplication Across Systems | Medium | ASSAY, REFINE, UNFURL |
| [UC-P02](02_product/UC-P02_uom_conflict_resolution.md) | UOM Conflict Resolution | Low | UNEARTH, REFINE |
| [UC-P03](02_product/UC-P03_variant_explosion.md) | Variant Explosion — Colour/Size as Separate Records | High | REFINE, UNFURL |
| [UC-P04](02_product/UC-P04_barcode_dq_failure.md) | Barcode DQ Failure — Invalid EAN/UPC | Low | ASSAY, UNEARTH |
| [UC-P05](02_product/UC-P05_cross_system_price_conflict.md) | Cross-System Price Conflict | Medium | REFINE, UNFURL, MARK |

#### Vendor
| Code | Title | Complexity | Key Stages |
|------|-------|-----------|------------|
| [UC-V01](03_vendor/UC-V01_legal_vs_trading_entity.md) | Legal vs Trading Entity Resolution | High | ASSAY, REFINE, UNFURL |
| [UC-V02](03_vendor/UC-V02_group_subsidiary_hierarchy.md) | Group/Subsidiary Hierarchy Conflict | High | REFINE, UNFURL, MARK |
| [UC-V03](03_vendor/UC-V03_tax_id_dq_failure.md) | Tax ID DQ Failure | Low | ASSAY, UNEARTH |
| [UC-V04](03_vendor/UC-V04_duplicate_vendor_detection.md) | Duplicate Vendor Detection | Medium | REFINE, UNFURL |
| [UC-V05](03_vendor/UC-V05_vendor_customer_crossover.md) | Vendor-Customer Crossover (Dual Role) | High | REFINE, UNFURL, MARK |

#### Asset
| Code | Title | Complexity | Key Stages |
|------|-------|-----------|------------|
| [UC-A01](04_asset/UC-A01_lifecycle_state_conflict.md) | Lifecycle State Conflict | Low | UNEARTH, REFINE |
| [UC-A02](04_asset/UC-A02_orphaned_asset_detection.md) | Orphaned Asset Detection | Low | UNEARTH |
| [UC-A03](04_asset/UC-A03_location_drift.md) | Location Drift | Medium | REFINE, UNFURL, MARK |
| [UC-A04](04_asset/UC-A04_serial_number_deduplication.md) | Serial Number Deduplication | Medium | ASSAY, REFINE |
| [UC-A05](04_asset/UC-A05_maintenance_lineage_break.md) | Maintenance Lineage Break | High | MARK, UNFURL |

#### Location
| Code | Title | Complexity | Key Stages |
|------|-------|-----------|------------|
| [UC-L01](05_location/UC-L01_hierarchy_conflict.md) | Hierarchy Conflict — Region vs Store Rollup | High | REFINE, UNFURL, MARK |
| [UC-L02](05_location/UC-L02_geocoding_drift.md) | Geocoding Drift — Null Island Detection | Low | UNEARTH |
| [UC-L03](05_location/UC-L03_store_warehouse_duplicate.md) | Store vs Warehouse Duplicate | Medium | REFINE, UNFURL |
| [UC-L04](05_location/UC-L04_address_standardisation.md) | Address Standardisation | Low | ASSAY, UNEARTH |
| [UC-L05](05_location/UC-L05_parent_child_resolution.md) | Parent-Child Location Resolution | High | REFINE, UNFURL, MARK |

#### Employee
| Code | Title | Complexity | Key Stages |
|------|-------|-----------|------------|
| [UC-E01](06_employee/UC-E01_multi_system_identity_merge.md) | Multi-System Identity Merge | Medium | ASSAY, REFINE, UNFURL |
| [UC-E02](06_employee/UC-E02_org_hierarchy_change.md) | Org Hierarchy Change — Reorg Impact | High | REFINE, UNFURL, MARK |
| [UC-E03](06_employee/UC-E03_multi_role_assignment.md) | Multi-Role Assignment | Medium | REFINE, UNFURL |
| [UC-E04](06_employee/UC-E04_leaver_rehire_detection.md) | Leaver-Rehire Detection | High | ASSAY, REFINE, MARK |
| [UC-E05](06_employee/UC-E05_cost_centre_realignment.md) | Cost Centre Realignment | Medium | REFINE, UNFURL, MARK |

#### Counterparty
| Code | Title | Complexity | Key Stages |
|------|-------|-----------|------------|
| [UC-CP01](07_counterparty/UC-CP01_dual_role_detection.md) | Dual-Role Detection — Vendor and Customer | High | REFINE, UNFURL, MARK |
| [UC-CP02](07_counterparty/UC-CP02_lei_validation_failure.md) | LEI Validation Failure | Low | ASSAY, UNEARTH |
| [UC-CP03](07_counterparty/UC-CP03_legal_entity_deduplication.md) | Legal Entity Deduplication | High | REFINE, UNFURL |
| [UC-CP04](07_counterparty/UC-CP04_jurisdiction_mismatch.md) | Jurisdiction Mismatch | Medium | UNEARTH, REFINE |
| [UC-CP05](07_counterparty/UC-CP05_relationship_lineage_audit.md) | Relationship Lineage Audit | High | MARK, UNFURL |

---

### Tier 2 — Cross-Domain Pairs (5 use cases)

| Code | Title | Domains | Complexity |
|------|-------|---------|-----------|
| [UC-XD01](08_cross_domain_pairs/UC-XD01_customer_product_purchase_history.md) | Customer × Product — Purchase History Integrity | Customer, Product | Medium |
| [UC-XD02](08_cross_domain_pairs/UC-XD02_asset_location_employee_triangle.md) | Asset × Location × Employee — The Ownership Triangle | Asset, Location, Employee | High |
| [UC-XD03](08_cross_domain_pairs/UC-XD03_vendor_product_sourcing_conflict.md) | Vendor × Product — Sourcing Conflict | Vendor, Product | Medium |
| [UC-XD04](08_cross_domain_pairs/UC-XD04_employee_location_org_hierarchy.md) | Employee × Location — Org Hierarchy mirrors Location Hierarchy | Employee, Location | High |
| [UC-XD05](08_cross_domain_pairs/UC-XD05_counterparty_vendor_customer_netoff.md) | Counterparty × Vendor × Customer — Treasury Net-Off | Counterparty, Vendor, Customer | High |

---

### Tier 3 — Grand Scenario (1 use case)

| Code | Title | Domains | Complexity |
|------|-------|---------|-----------|
| [UC-GS01](09_grand_scenario/UC-GS01_new_store_opening.md) | New Store Opening — All 7 Domains in One Event | **All 7** | ⭐⭐⭐ GRAND |

---

## How to Run the Scenarios

All scenarios use the sample data in `shared/sample_data/output/`. Generate it first:

```bash
cd ~/Projects/AURUM
source .venv/bin/activate
python shared/sample_data/generate_all.py
```

**Run single-domain scenarios:**
```bash
# ASSAY — inspect a domain's raw data
python -m runtimes.cli assay shared/sample_data/output/customers_dirty.csv
python -m runtimes.cli assay shared/sample_data/output/vendors_dirty.csv

# UNEARTH — profile for DQ issues
python -m runtimes.cli unearth customer shared/sample_data/output/customers_dirty.csv
python -m runtimes.cli unearth product shared/sample_data/output/products_dirty.csv
python -m runtimes.cli unearth vendor shared/sample_data/output/vendors_dirty.csv
python -m runtimes.cli unearth asset shared/sample_data/output/assets_dirty.csv
python -m runtimes.cli unearth location shared/sample_data/output/locations_dirty.csv
python -m runtimes.cli unearth employee shared/sample_data/output/employees_dirty.csv
python -m runtimes.cli unearth counterparty shared/sample_data/output/counterparties_dirty.csv

# ANOMALY DETECTION — ML-based flagging
python -m runtimes.cli anomaly shared/sample_data/output/customers_dirty.csv --domain customer

# FULL PIPELINE — ASSAY → UNEARTH → REFINE → UNFURL → MARK
python -m runtimes.cli demo
python demo/end_to_end_demo.py
```

**HTTP API (FastAPI):**
```bash
uvicorn runtimes.api.main:app --reload --port 8000
# Docs: http://localhost:8000/docs

curl -F file=@shared/sample_data/output/customers_dirty.csv http://localhost:8000/unearth/customer
curl -F file=@shared/sample_data/output/vendors_dirty.csv http://localhost:8000/unearth/vendor
```

**MCP Server (Claude Code / Cursor / Hermes):**
```bash
python runtimes/mcp/server.py
# Tools: assay_schema, unearth_profile, refine_match
```

---

## How to Contribute

New use cases are welcome! Follow the template in any existing UC-*.md file:

1. Summary → Business Impact → Scenario Setup → Example Records
2. AURUM Pipeline Walk-Through (one section per stage)
3. Stewardship Decision Point → Expected Golden Record → CLI Demo Command

File naming: `UC-[DOMAIN_CODE][NN]_short_name.md`

Domain codes: `C` Customer, `P` Product, `V` Vendor, `A` Asset, `L` Location, `E` Employee, `CP` Counterparty, `XD` Cross-Domain, `GS` Grand Scenario.

Submit a PR — see [CONTRIBUTING.md](../CONTRIBUTING.md).
