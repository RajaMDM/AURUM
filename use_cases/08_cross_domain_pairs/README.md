# Cross-Domain Pairs — Use Cases

Real enterprise MDM never stays within a single domain. These use cases show **2–3 domains talking to each other** — where a golden record in one domain is a foreign key in another, and inconsistency in one domain ripples into another.

## Use Cases

| Code | Title | Domains | Complexity | Key Stages |
|------|-------|---------|-----------|------------|
| [UC-XD01](UC-XD01_customer_product_purchase_history.md) | Customer × Product — Purchase History Integrity | Customer, Product | Medium | REFINE, UNFURL, MARK |
| [UC-XD02](UC-XD02_asset_location_employee_triangle.md) | Asset × Location × Employee — The Ownership Triangle | Asset, Location, Employee | High | REFINE, UNFURL, MARK |
| [UC-XD03](UC-XD03_vendor_product_sourcing_conflict.md) | Vendor × Product — Sourcing Conflict | Vendor, Product | Medium | UNEARTH, REFINE, UNFURL |
| [UC-XD04](UC-XD04_employee_location_org_hierarchy.md) | Employee × Location — Org Hierarchy mirrors Location Hierarchy | Employee, Location | High | REFINE, UNFURL, MARK |
| [UC-XD05](UC-XD05_counterparty_vendor_customer_netoff.md) | Counterparty × Vendor × Customer — Treasury Net-Off | Counterparty, Vendor, Customer | High | REFINE, UNFURL, MARK |
