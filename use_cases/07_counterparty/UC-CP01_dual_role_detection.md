# UC-CP01: Dual-Role Detection — Same Entity as Vendor and Customer

## Summary
Zephyr Air appears in the CRM as a corporate customer (they buy business-class loungewear from the company) and in the ERP vendor master as a supplier (they provide chartered freight services). Two records, one legal entity, zero linkage. Treasury needs to know the net financial exposure. Legal needs one contract register entry. And any sanctions screening must cover both roles simultaneously — not just one.

## Domain
Counterparty

## AURUM Stage(s)
REFINE · UNFURL · MARK

## Business Impact
- Netting-off opportunity missed: AED 800K receivable from Emirates (customer) vs AED 1.2M payable to Emirates (vendor) — net exposure AED 400K, but finance sees two separate balances
- Sanctions screening: if one role is screened and the other isn't, regulatory exposure is severe (UAE AML/CFT law)
- Contract management: two contract teams may negotiate conflicting terms with the same legal entity
- Credit risk: credit limit set for the customer role only — doesn't offset the payable position

## Scenario Setup
CRM record: `Zephyr Air PJSC` (customer, `CUST-00445`). ERP vendor record: `Zephyr Airlines` (vendor, `VEND-00231`). Same LEI (`549300EXAMPLE0000001`), different name spelling, different teams managing each.

## Example Records

| field | CRM CUST-00445 | ERP VEND-00231 |
|-------|----------------|----------------|
| legal_name | Zephyr Air PJSC | Zephyr Airlines |
| lei_code | 549300EXAMPLE0000001 | 549300EXAMPLE0000001 |
| role | Customer | Vendor |
| jurisdiction | UAE | AE |
| contact | wholesale@emirates.com | freight@emirates.com |
| relationship_value | AED 800K AR | AED 1.2M AP |

## AURUM Pipeline Walk-Through

**ASSAY** — Customer and Vendor records ingested from different source systems. LEI field present in both.

**UNEARTH** — Counterparty profiler: LEI exact match across customer and vendor datasets → `DUAL_ROLE_DETECTED` flag, HIGH severity. This is not an error — it's a critical data relationship.

**REFINE** — Cross-domain link established (not a merge): `CUST-00445 ↔ VEND-00231` linked as same legal entity. Both golden records maintained separately with `counterparty_link_id` pointing to each other. `dual_role: true` flagged on both.

**UNFURL** — Treasury receives the linked view: net exposure = AED 400K payable. Compliance team receives the dual-role flag for simultaneous screening. Legal contract team notified.

**MARK** — `DUAL_ROLE_LINK(GLD-CUST-00445 ↔ GLD-VEND-00231, LEI=549300EXAMPLE0000001, net_exposure=AED_400K)` logged.

## Stewardship Decision Point
Nadia (Governance) and Tariq (Security) jointly review. Nadia confirms the netting-off policy applies. Tariq ensures both roles are included in the next sanctions screening run. Treasury sets up the net credit facility.

## Expected Golden Record
Two linked golden records:
- `GLD-CUST-00445`: `dual_role: true`, `linked_vendor_id: GLD-VEND-00231`
- `GLD-VEND-00231`: `dual_role: true`, `linked_customer_id: GLD-CUST-00445`

## CLI Demo Command
```bash
python -m runtimes.cli unearth counterparty shared/sample_data/output/counterparties_dirty.csv
```

## Related Use Cases
- [UC-V05](../03_vendor/UC-V05_vendor_customer_crossover.md) — Vendor-Customer crossover at the Vendor domain level
- [UC-CP05](UC-CP05_relationship_lineage_audit.md) — Audit trail for dual-role relationships
