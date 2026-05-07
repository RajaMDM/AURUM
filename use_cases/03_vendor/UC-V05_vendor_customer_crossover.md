# UC-V05: Vendor-Customer Crossover (Dual Role)

## Summary
"Noon.com" is both a major e-commerce marketplace customer (they buy wholesale product from the company) AND a distribution vendor (the company sells through Noon's platform and receives commission payments). The ERP has two separate records — one in the Customer master, one in the Vendor master — with no linkage. This dual-role blind spot creates credit limit miscalculations, netting-off failures, and incomplete 360° relationship views.

## Domain
Vendor / Customer (Cross-domain)

## AURUM Stage(s)
REFINE · UNFURL · MARK

## Business Impact
- Credit limit set for the customer entity only — doesn't account for amounts owed BY the company to Noon as vendor
- Netting-off opportunity missed: AED 200K owed to Noon (vendor) vs AED 150K owed by Noon (customer) — net exposure is only AED 50K, but finance sees two separate balances
- Relationship management: account manager and vendor manager don't know they're managing the same legal entity
- Regulatory: AML netting and offset arrangements require identification of dual-role counterparties

## Scenario Setup
CRM has `Noon.com FZ-LLC` as a customer (`CUST-00890`). ERP Vendor master has `Noon E-Commerce LLC` as vendor (`VEND-00445`). Same TRN, different name variants, different teams managing each.

## Example Records

| field | CRM CUST-00890 | ERP VEND-00445 |
|-------|----------------|----------------|
| entity_name | Noon.com FZ-LLC | Noon E-Commerce LLC |
| tax_id | TRN100789001234 | TRN100789001234 |
| role | Customer | Vendor |
| city | Dubai | Dubai |
| contact_email | wholesale@noon.com | vendor-mgmt@noon.com |
| relationship_value | AED 150,000 AR | AED 200,000 AP |

## AURUM Pipeline Walk-Through

**ASSAY** — Customer record ingested from CRM. Vendor record from ERP. Different source systems, different schemas — both mapped to canonical entity schema.

**UNEARTH** — Cross-domain TRN check: `TRN100789001234` appears in BOTH customer and vendor datasets → `DUAL_ROLE_DETECTED` flag raised.

**REFINE** — Cross-domain cluster: `CUST-00890` and `VEND-00445` linked as the same legal entity with dual roles. NOT merged into one record (they serve different functions) but LINKED with `related_entity_id`.

**UNFURL** — Both golden records published. `GLD-CUST-00890.related_vendor_id = GLD-VEND-00445` and vice versa. Finance system receives the linkage for netting calculations.

**MARK** — `DUAL_ROLE_LINK(GLD-CUST-00890 ↔ GLD-VEND-00445, TRN=TRN100789001234)` logged.

## Stewardship Decision Point
Steward confirms the linkage is intentional (not an error) and notifies the finance team to implement netting-off for this counterparty. The credit team updates the limit to reflect the net position.

## Expected Golden Record
Two linked records:
- `GLD-CUST-00890`: `legal_name: Noon.com FZ-LLC`, `role: Customer`, `related_vendor_id: GLD-VEND-00445`
- `GLD-VEND-00445`: `legal_name: Noon E-Commerce LLC`, `role: Vendor`, `related_customer_id: GLD-CUST-00890`

## CLI Demo Command
```bash
python -m runtimes.cli demo
```

## Related Use Cases
- [UC-CP01](../07_counterparty/UC-CP01_dual_role_detection.md) — Dual role detection in the Counterparty domain
- [UC-V04](UC-V04_duplicate_vendor_detection.md) — Duplicate vendor detection
