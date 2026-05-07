# UC-V04: Duplicate Vendor Detection

## Summary
"Al Zafra Office Supplies" was entered twice in the ERP — once by the Dubai procurement team and once by the Abu Dhabi office, each unaware of the other. Both records have been used for purchase orders. The company is now paying two different bank accounts for what may be the same vendor — a classic duplicate payment risk that also opens a fraud vector.

## Domain
Vendor

## AURUM Stage(s)
REFINE · UNFURL · MARK

## Business Impact
- Duplicate payments: the same invoice may be paid against both vendor records
- Fraud risk: if one vendor account has been compromised, the attacker may create a near-duplicate
- Spend analytics incorrect — total spend with this supplier is split
- Supplier relationship management: two account managers potentially managing the same supplier

## Scenario Setup
Dubai procurement team created `ERP-V301` with trading name "Al Zafra Office Supplies" and email `info@albaraka.ae`. Abu Dhabi team created `ERP-V302` with legal name "Al Zafra Office Supplies LLC" and email `accounts@albaraka.ae`. Same physical address, different email contacts, different bank accounts on file.

## Example Records

| field | ERP-V301 | ERP-V302 |
|-------|----------|----------|
| legal_name | Al Zafra Office Supplies | Al Zafra Office Supplies LLC |
| trading_name | Al Zafra | Al Zafra Supplies |
| tax_id | | TRN100567890001234 |
| contact_email | info@albaraka.ae | accounts@albaraka.ae |
| city | Dubai | Abu Dhabi |
| bank_account | AE12 0330 0000 1234 5678 901 | AE98 0340 0000 9876 5432 100 |
| payment_terms | Net 45 | Net 30 |

## AURUM Pipeline Walk-Through

**ASSAY** — Both records ingest from the same ERP source. No TRN on `ERP-V301` to use as anchor.

**UNEARTH** — Vendor profiler: `ERP-V301` flagged for missing TRN. Email domain `@albaraka.ae` matches across both records — flagged as potential duplicate signal.

**REFINE** — Matcher: name similarity `Al Zafra Office Supplies` vs `Al Zafra Office Supplies LLC` = 0.92. Email domain match. BUT city differs (Dubai vs Abu Dhabi) and bank accounts differ — match score 0.81 (above 0.75 threshold but below 0.90 auto-merge threshold). Flagged as `PROBABLE_DUPLICATE` for steward review.

**UNFURL** — Not merged automatically. Both records held in `PENDING_STEWARD_REVIEW` state. Steward notified with side-by-side comparison.

**MARK** — `DUPLICATE_CANDIDATE(ERP-V301, ERP-V302, score=0.81, reason=name+email_domain)` logged.

## Stewardship Decision Point
HIGH priority — different bank accounts are the key risk signal. Steward must:
1. Verify with the supplier which bank account is correct
2. Confirm if Dubai/Abu Dhabi offices are the same legal entity or genuinely separate
3. Either MERGE (same entity, consolidate to one bank account) or SPLIT (genuinely different trading entities)

## Expected Golden Record
If merged: `GLD-VEND-0301`, `legal_name: Al Zafra Office Supplies LLC`, TRN from V302, bank account verified by steward.

## CLI Demo Command
```bash
python -m runtimes.cli demo
```

## Related Use Cases
- [UC-V01](UC-V01_legal_vs_trading_entity.md) — Legal vs trading entity (overlapping scenario)
- [UC-V03](UC-V03_tax_id_dq_failure.md) — Missing TRN that obscures duplicate detection
