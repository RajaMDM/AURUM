# UC-XD05: Counterparty × Vendor × Customer — Treasury Net-Off

## Domains
Counterparty · Vendor · Customer

## Summary
Majid Al Futtaim (MAF) Group is simultaneously:
- A **customer** (MAF Retail buys corporate gifting products from the company)
- A **vendor** (MAF's logistics arm delivers goods to the company's stores)
- A **counterparty** (MAF has a treasury FX forward contract with the company)

Three domains. One legal entity. Three separate financial exposures that must be viewed and managed as a single net position for credit risk, regulatory reporting, and relationship management. AURUM links all three golden records and surfaces the unified exposure to Treasury.

## Business Impact
- Credit risk: net exposure = AR (customer) + FX mark-to-market (counterparty) - AP (vendor). Without the link, credit committee sees three unrelated entries — total exposure understated or overstated
- Basel III large exposure rule: if total exposure to a single entity (across all roles) exceeds 25% of Tier 1 capital, it must be reported. Fragmented records mean the threshold is never triggered — regulatory breach
- Relationship strategy: the CEO negotiating a new deal with MAF has no visibility that the company also owes MAF AED 1.5M in payables — negotiating from a position of false strength
- Sanctions: if MAF were added to a sanctions list, all three exposures must be frozen simultaneously

## Scenario Setup

| Domain | Record | Role | Exposure |
|--------|--------|------|----------|
| Customer | GLD-CUST-00890 | MAF Retail (buyer) | AED 850K receivable |
| Vendor | GLD-VEND-00445 | MAF Logistics (supplier) | AED 1.5M payable |
| Counterparty | GLD-CP-00789 | MAF Treasury (FX forward) | AED 200K MTM gain |

Same TRN (`TRN100456789001234`) and LEI (`MAFIUAE2024EXAMPLE01`) across all three.

## AURUM Pipeline Walk-Through

**Cross-Domain UNEARTH** — TRN and LEI appear across Customer, Vendor, and Counterparty datasets → `MULTI_DOMAIN_ENTITY` detected. All three share same legal entity identifiers.

**Cross-Domain REFINE** — Three-way link established:
- `GLD-CUST-00890 ↔ GLD-VEND-00445 ↔ GLD-CP-00789`
- Link type: `SAME_LEGAL_ENTITY`
- Each golden record retains its domain identity — not merged flat
- Net exposure calculated: AED 850K (AR) - AED 1.5M (AP) + AED 200K (MTM) = **AED -450K net payable to MAF**

**UNFURL** — Treasury receives the unified MAF exposure dashboard:
```
MAF Group — Unified Exposure
  Customer (MAF Retail):       AED +850K  AR
  Vendor (MAF Logistics):      AED -1.5M  AP
  Counterparty (FX Forward):   AED +200K  MTM
  ─────────────────────────────────────────
  NET POSITION:                AED -450K  (net payable)
```

**MARK** — `MULTI_DOMAIN_LINK(GLD-CUST-00890 ↔ GLD-VEND-00445 ↔ GLD-CP-00789, TRN=TRN100456789001234, net_exposure=AED-450K)` logged. Credit committee notified for limit review.

## Stewardship Decision Point
Nadia (Governance) and Tariq (Security) jointly sign off the three-way link. Treasury CFO reviews the net exposure — confirms netting agreement is in place with MAF. Credit limit updated to reflect net position. Basel III large exposure calculation re-run with the correct consolidated exposure.

## Validated Three-Domain View

```
MAF Group (Legal Entity)
├── as Customer ──▶ GLD-CUST-00890
│                    └── AR: AED 850K | Loyalty: Gold | Account Mgr: Amara
│
├── as Vendor ────▶ GLD-VEND-00445
│                    └── AP: AED 1.5M | Category: Logistics | Procurement: Carlos
│
└── as Counterparty ▶ GLD-CP-00789
                      └── FX Forward MTM: AED 200K | LEI verified | Screened: CLEAR
```

## CLI Demo Command
```bash
python -m runtimes.cli demo
```

## Related Use Cases
- [UC-CP01](../07_counterparty/UC-CP01_dual_role_detection.md) — Dual-role (two domains) — simpler version of this
- [UC-V05](../03_vendor/UC-V05_vendor_customer_crossover.md) — Vendor-Customer crossover
- [UC-GS01](../09_grand_scenario/UC-GS01_new_store_opening.md) — Grand scenario: all 7 domains linked
