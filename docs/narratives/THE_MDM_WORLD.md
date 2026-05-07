# Imagine a World Where Your Data Actually Knows Itself

> *Authored by Inaayah, Technical Writer — AURUM Project*
> *Reviewed by Shazia (DQ Lead), Pierre (EA Head), Arun (BI Head)*
> *With scenarios drawn from the AURUM use-case library*

---

## Before You Begin — A Word About This Document

This is not a technical manual. Well — it *is* a technical document, but it's dressed for the real world.

It is written for the data practitioner who has sat in a Monday morning meeting watching three different spreadsheets argue with each other. For the CTO who has watched a "data integration project" take 18 months and still not produce a single trustworthy number. For the business analyst who has manually deduped a customer list in Excel, *again*, for the fifth quarter in a row.

It's also written for the engineer who wants to understand *why* MDM is hard — not just that it's hard.

We will walk through **four acts** — four stages in the journey from raw chaotic data to a living, talking, self-aware data estate. In each act, we will show you:

- **🔴 The world without MDM** — told as a story, because data problems are human problems
- **🟢 The world with MDM** — the same story, different ending
- **🔧 The technical reality** — what AURUM is actually doing under the hood

And in each act, we will be honest: **MDM at each stage still leaves problems unsolved**. The promise of MDM is not that it fixes everything at once. The promise is that it fixes the right things in the right order, and makes the next thing fixable.

Let's begin.

---

# ACT I — THE ISLAND: Single Domain, Standing Alone

## What Is a Domain, Really?

In MDM, a **domain** is a category of master data that describes a core business entity. Not transactions — those are operational. Not reports — those are derived. A domain is a *thing your business cares about deeply enough to manage as a single source of truth.*

The seven domains in AURUM are:

| Domain | The Thing | The Core MDM Question |
|--------|-----------|----------------------|
| **Customer** | Who buys from you | Are these two records the same person? |
| **Product** | What you sell | Are these two SKUs the same thing? |
| **Vendor** | Who supplies you | Is this a legal entity or a trading name? |
| **Asset** | What you own | Is this laptop the same one that was serviced last month? |
| **Location** | Where things happen | Is "Dubai Mall Store" and "Dubai Mall" the same place? |
| **Employee** | Who works for you | Are these three AD/HRMS/Payroll records the same person? |
| **Counterparty** | Who you have financial exposure to | Is this vendor also your customer? |

In Act I, we master **one domain at a time**. We don't connect them. We don't make them talk to each other. We just make one of them clean, golden, and trustworthy.

This is where most MDM programmes begin. And for good reason — it is hard enough.

---

## The Customer Domain — Standing Alone

### 🔴 Without MDM: The Life of Priya Sharma

Priya Sharma is a loyal customer. She has been buying from you for four years. She spends, on average, AED 12,000 a year. She is Gold tier. She deserves your best service.

But in your systems, Priya is three different people.

- In the **CRM**, she is `Priya Sharma`, email `priya.sharma@meridian.com`, registered from the Dubai store in 2020.
- In the **ECOMM platform**, she is `PRIYA SHARMA`, email `PRIYA.SHARMA@meridian.com`, registered online in 2021. The system treated the uppercase email as a different account.
- In the **Loyalty system**, she is `priya sharma` (all lowercase), email `priyasharma@meridian.com` (no dot, a typo on sign-up day), with Gold tier because she earned it at an in-store event.

**What this means in practice:**

The marketing team runs a VIP promotion for Gold-tier customers. Their query hits the Loyalty system — Priya gets the email. But then the CRM team runs a "re-engagement" campaign for customers who haven't purchased in 90 days — and CRM Priya hasn't, because her purchases are split across ECOMM and Loyalty. She gets a "we miss you" email. *Two emails in two days.* She notices.

The customer service agent who handles her complaint sees the CRM record: no ECOMM purchases, no loyalty points. She looks incomplete — a small customer. The agent offers a standard resolution. Priya escalates.

Meanwhile, the analytics team is reporting **3.2 million unique customers**. The real number is closer to 2.6 million. CLV models are wrong. Churn predictions are wrong. Segment targeting is wrong. All downstream from the same root cause: Priya Sharma is three people.

**The cost:**
- Duplicate marketing spend (3× the email cost)
- Damaged customer relationship (Gold-tier customer treated as low-value)
- Wrong business decisions (based on inflated customer count)
- GDPR/PDPL exposure (if Priya requests data erasure, you can only erase one of her three records)

---

### 🟢 With MDM — Customer Domain Only

AURUM's Customer domain MDM runs. Here is what happens to Priya:

**ASSAY:** Three records ingested from CRM, ECOMM, LOYALTY. Fields mapped to canonical customer schema. Email case variants flagged. Phone format variants normalised.

**UNEARTH:** DQ rules fire. Email `PRIYA.SHARMA@meridian.com` normalised to lowercase. `priyasharma@meridian.com` flagged as a possible variant (missing dot). Phone `00971-50-1234567` normalised to `+971501234567`. LOYALTY record flagged: email differs from CRM/ECOMM pattern — steward attention requested.

**REFINE:** Matcher runs. CRM vs ECOMM: name similarity 0.97, normalised email exact match → MATCH (score 0.98). CRM vs LOYALTY: name exact match, email similarity 0.79, phone match → PROBABLE MATCH (0.84). All three records form one cluster. Survivorship: CRM email (most complete, correct format), ECOMM phone (the only phone), LOYALTY tier (Gold — highest trust source for tier).

**UNFURL:** Golden record `GLD-CUST-00101` published. **One Priya.** One customer ID that all systems can reference. Trust score: 0.87.

**MARK:** Lineage logged. Every source record linked to the golden record. Every decision recorded.

**What changes in practice:**

The marketing team runs their VIP campaign. One email goes to Priya — the right one, with her full purchase history aggregated. Her CLV is now correctly calculated as AED 12,000/year across all channels. The "re-engagement" campaign correctly excludes her — she's active.

When Priya calls customer service, the agent sees one complete record: Gold tier, 4 years, all purchases, all interactions. She is treated accordingly.

The analytics team reports **2.6 million unique customers**. The business makes better decisions.

If Priya requests data erasure under GDPR/PDPL, one deletion on `GLD-CUST-00101` cascades to all three source records via the lineage trail.

---

### 🔧 Technical: What AURUM Is Doing

```
Source Records:
  CRM-00101     → first_name: "Priya",       email: "priya.sharma@meridian.com"
  ECOMM-00234   → first_name: "PRIYA",       email: "PRIYA.SHARMA@meridian.com"
  LOYALTY-00089 → first_name: "priya",       email: "priyasharma@meridian.com"

UNEARTH normalisation:
  email.lower()          → "priya.sharma@meridian.com" (CRM/ECOMM match)
  email similarity       → "priya.sharma" vs "priyasharma" = 0.79 (Jaro-Winkler)

REFINE matching (composite score):
  name_similarity(RapidFuzz token_sort) = 0.97
  email_similarity(normalised)          = 1.0   [CRM vs ECOMM]
  phone_match(normalised)               = 1.0   [CRM vs ECOMM]
  cluster_score                         = 0.98  → MATCH

  name_similarity                       = 0.95  [CRM vs LOYALTY]
  email_similarity(normalised)          = 0.79  [CRM vs LOYALTY]
  cluster_score                         = 0.84  → PROBABLE_MATCH (above 0.75 threshold)

REFINE survivorship:
  first_name  → "Priya"      (CRM — modal after normalisation)
  email       → "priya.sharma@meridian.com" (CRM/ECOMM consensus, valid format)
  phone       → "+971501234567" (ECOMM — only source with a phone)
  loyalty_tier → "Gold"     (LOYALTY — designated system of record for tier)

MARK lineage events:
  INGESTED(CRM-00101, ECOMM-00234, LOYALTY-00089)
  MATCHED(CRM-00101 ↔ ECOMM-00234, score=0.98)
  MATCHED(CRM-00101 ↔ LOYALTY-00089, score=0.84)
  GOLDEN_ASSEMBLED(GLD-CUST-00101, trust=0.87)
```

The RapidFuzz + Jaro-Winkler composite scorer is domain-agnostic. The survivorship rules (which source wins for which field) are configurable per domain. The lineage tracker is append-only.

---

### ⚠️ What Act I Still Leaves Broken

Customer domain is clean. But:

- **Products** are still duplicated. Priya's purchase history references 4 different SKU records for the same headphones.
- **Location** is still fragmented. The Dubai Mall store has 3 different location records in 3 systems.
- **Employees** aren't linked. The customer service agent who handled Priya's complaint is in HRMS but not in CRM — no 360° service view.

The island is clean. The ocean around it is still chaos.

---

## The Product Domain — Standing Alone

### 🔴 Without MDM: The Warehouse Manager's Wednesday

Ahmed is a warehouse manager. He runs the Sharjah distribution centre. Every Wednesday morning he prints the replenishment report.

This morning the report says: **SKU-0042: 14 units in stock**. He checks physically — he counts 47. The number in the system is wrong. It has been wrong for six months.

Why? Because `SKU-0042`, `sku_0042`, `SKU0042`, and ` SKU-0042` (with a leading space) are all the same physical product — Wireless Headphones Pro — but the WMS tracks them as four separate SKUs. When stock comes in under one variant and goes out under another, the counts diverge. Ahmed has learned to distrust the system. He keeps his own spreadsheet.

Meanwhile, in pricing:
- ERP has the price as AED 299
- ECOMM has it at AED 279 (a promotion that was never reverted)
- The marketplace partner has it at AED 319

A customer buys online at 279, picks up in-store where the till rings up 299. The cashier manually overrides. The customer is confused. The audit trail shows two different prices for the same transaction.

In the category management team, the product appears four times in the portfolio report. Four rows. Four sets of sales numbers. The category manager can't tell which one is correct. She presents the wrong number to the buying director. A purchasing decision is made on false data.

---

### 🟢 With MDM — Product Domain Only

AURUM normalises SKU-0042 across all four format variants. One golden product record. One canonical SKU. One price (AED 299, ERP is the system of record for RRP). ECOMM receives the corrected price via reverse sync. Ahmed's stock count reconciles — 47 units, correctly tracked as one SKU. The category report has one row, one number.

The category manager presents the right number. The right buying decision is made.

---

### 🔧 Technical: SKU Normalisation

```python
# AURUM normalises SKU variants before matching
def normalise_sku(raw: str) -> str:
    return raw.strip().lower().replace("-", "").replace("_", "")

normalise_sku("SKU-0042")  → "sku0042"
normalise_sku("sku_0042")  → "sku0042"
normalise_sku("SKU0042")   → "sku0042"
normalise_sku(" SKU-0042") → "sku0042"  # leading space stripped

# Post-normalisation: all four are identical → exact match → cluster
# Survivorship: PIM record wins (highest source trust for product attributes)
# Canonical SKU output: "SKU-0042" (PIM format)
```

---

## The Vendor Domain — Standing Alone

### 🔴 Without MDM: Paying the Same Supplier Twice

The accounts payable team processes invoices. This week, they receive two invoices — one from "EmiratesTech" (AED 45,000) and one from "Emirates Tech Solutions LLC" (AED 45,000). Same amount, suspiciously similar supplier names. Different bank accounts.

Are these the same? Is it a duplicate invoice? Or two separate suppliers who happen to charge the same amount this week?

The AP clerk raises a query. It sits in an email chain for four days. Both invoices are due. To avoid a late payment penalty, both are paid. It is later discovered they are the same entity — the same vendor registered under a trading name in ERP and a legal name in the procurement system. AED 45,000 overpaid.

The finance team spends three days recovering the duplicate payment. The vendor's accounts receivable team is confused — they applied the payment to an open invoice, then received a second payment against the same invoice and issued a credit note. The credit note sits unreconciled for two quarters.

---

### 🟢 With MDM — Vendor Domain Only

AURUM identifies `EmiratesTech` and `Emirates Tech Solutions LLC` as the same legal entity (matched on TRN `TRN100234567003`, name similarity 0.87, same city/country). One golden vendor record. One bank account (verified by steward). The AP system sees one vendor — the second invoice triggers a duplicate payment warning before it is processed.

The AED 45,000 stays in the company's account.

---

## The Asset Domain — Standing Alone

### 🔴 Without MDM: The Ghost Fleet

The finance team is preparing the year-end accounts. Fixed asset register: 1,247 assets. Book value: AED 8.3 million.

The physical audit team goes out. They can only locate 1,089 assets. 158 assets cannot be found. Some are listed as "Active" in the system. Some are listed at locations that no longer exist (a store that closed 18 months ago).

Are they stolen? Misplaced? Were they disposed of and never written off? No one knows. Each scenario has different accounting treatment, different insurance implications, different police reporting requirements.

The auditors qualify the accounts. The CFO is embarrassed. The asset register has become a fiction.

---

### 🟢 With MDM — Asset Domain Only

AURUM's orphan detection flags 142 assets with no location_id and no assigned_to. The lifecycle state inconsistency detector flags 67 assets with conflicting states across CMDB and FM. The serial number deduplication catches 14 records that are likely the same physical asset registered twice after a CMDB migration.

The steward team — led by Jin — runs a systematic physical audit against the AURUM orphan report. 142 becomes 8 (confirmed missing, police reported, written off). The fixed asset register is accurate. The year-end accounts are clean.

---

## The Location Domain — Standing Alone

### 🔴 Without MDM: The Store That Doesn't Exist

A customer calls in — she wants to know if the Dubai Hills Mall store is open on Fridays. The customer service agent looks it up. In the CRM, the store is listed as "Dubai Hills Mall Store" under the UAE hierarchy. In the store locator app (powered by YEXT), it appears as "Dubai Hills" with no parent region. The agent gives the Friday hours for the wrong store — the hours in YEXT are for a different location with a similar name.

The customer drives there on Friday. It's closed until 2pm (Friday prayer hours). She waited 30 minutes. She posts about it.

Meanwhile, the regional VP runs a revenue report by location. The Dubai Hills Mall store's revenue appears in "GCC Retail" in YEXT but in "UAE North" in ERP. The same store's numbers are in two buckets. The Emirate-level rollup is wrong. Budget variance reporting is wrong.

---

### 🟢 With MDM — Location Domain Only

One golden location record for every physical place. One hierarchy — UAE → Dubai → Downtown Dubai → Store. The store locator, the CRM, and the ERP all see the same record, the same hours, the same parent. The customer gets the right answer. The VP gets the right report.

---

## The Employee Domain — Standing Alone

### 🔴 Without MDM: The Security Nightmare

An employee leaves the company. HR updates the HRMS — status: Inactive. But:
- Active Directory account: still active (IT uses a separate offboarding checklist that's 2 days behind)
- Payroll: still on the run (payroll cutoff was yesterday — they'll get one more month's salary)
- ERP project system: still listed as project owner on 3 active projects

The ex-employee's laptop is returned. But their AD account — with access to SharePoint, ERP, and the customer database — is still live for 48 hours. In a regulated environment, that's a reportable breach.

On the re-hire side: Lena rejoins. A new employee ID is created. No one searched for her old record. Her 3-year service history, her previous manager relationships, her original hire date — all orphaned on a retired record. Her pension entitlements will be miscalculated. Long-service award eligibility will be wrong.

---

### 🟢 With MDM — Employee Domain Only

AURUM's JML (Joiner-Mover-Leaver) detection flags Lena's new record as a probable rehire (email match on inactive record). The steward confirms. One linked golden record — predecessor/successor chain. Service history intact.

For the leaver: AURUM detects that the HRMS inactive flag has not propagated to AD or Payroll. Cross-system consistency alert raised. Offboarding checklist triggered automatically for all linked systems.

---

## The Counterparty Domain — Standing Alone

### 🔴 Without MDM: The Sanctions Nightmare

The compliance team screens all counterparties quarterly against OFAC, UN, and UAE Central Bank sanctions lists. They use the COMPLIANCE system — which has 340 counterparty records.

But TREASURY has 280 counterparty records. Some are the same legal entities as in COMPLIANCE, some are different records for the same entities, some are unique to TREASURY.

The screening runs against COMPLIANCE only — because that's the "official" system. TREASURY records are never screened. If a sanctioned entity exists only in TREASURY (because they do FX forwards but not trade finance), they have never been screened.

This is a regulatory breach. In the UAE, AML/CFT violations carry fines up to AED 1 million per transaction.

---

### 🟢 With MDM — Counterparty Domain Only

AURUM creates one golden counterparty record for each legal entity — reconciling COMPLIANCE and TREASURY records by LEI. The sanctions screening runs against the golden record set. All exposures — trade finance, FX, treasury, and commercial — are screened together. No gaps.

---

## ⚠️ What Act I Leaves Us With

After mastering all seven domains **independently**, here is where we stand:

**✅ What works:**
- Each domain is internally consistent
- No duplicates within any domain
- DQ issues are detected and remediated
- Golden records exist for each domain
- Stewardship workflows are running

**❌ What still breaks:**
- A **customer's purchase history** still references old SKU source IDs — not the golden product IDs
- An **employee's assigned assets** still reference the old FM location code — not the golden location ID
- A **vendor's approved product list** has duplicates because two vendor records (now one golden record) each had an AVL entry
- The **store opening use case** fails: you can't assign employees to a location, provision assets to a store, or list products by location — because none of the domain golden records are linked to each other

The islands are clean. But they are still islands.

---

# ACT II — SEVEN CLEAN SILOS: All Domains Mastered, None Connected

## The Illusion of Progress

There is a dangerous moment in every MDM programme when the team celebrates too early.

*"We've mastered the Customer domain!"*
*"Product MDM is live!"*
*"All seven domains have golden records!"*

These are real achievements. But if each domain is mastered in isolation — with no cross-domain linkage — the business has not yet realised the full value of MDM. It has built seven clean islands with no bridges between them.

This is **Act II**: all domains mastered, golden records everywhere, but none of them talking to each other.

---

## 🔴 The World Before Act II: The Seven-Way Chaos

Let us paint the pre-MDM picture across all seven domains simultaneously.

**Monday morning. The executive team meeting.**

The CEO asks: *"What is our total exposure to Majid Al Futtaim Group?"*

The CFO pulls up three screens:
- **CRM:** MAF is a customer. Receivable: AED 850K. But is this the parent group or a subsidiary? Unclear.
- **ERP Vendor:** "MAF Retail LLC" is a supplier. Payable: AED 1.5M. Is this the same entity as the CRM customer? Unknown.
- **Treasury:** "MAF" has an FX forward. MTM: AED 200K gain. Is this the same MAF? The LEI doesn't match the others — one has a placeholder LEI.

The CFO cannot answer the question. She gives a range: "Between AED 200K net gain and AED 2.55M combined, depending on which entities are the same."

The CEO's follow-up: *"And how many products does MAF retail for us, and at which stores?"*

The Product team: products are in PIM. The Location team: stores are in YEXT and ERP. The Vendor team: MAF as a marketplace vendor is in PROCUREMENT. None of these systems share a common ID.

The answer takes three days to compile. It's probably wrong.

**Meanwhile, across the business:**

- The **asset management** team can't reconcile their CMDB with the location master. Locations in the asset register are LOC-001, LOC-R02, LOC-W01 — some of these were merged into single golden location records by Location MDM, but the asset system wasn't told.
- The **HR team** can't find which employee is assigned to the Dubai Hills store — because Employee MDM didn't update the `location_id` field to the new golden location ID.
- The **supply chain** team can't determine which vendors supply which stores — because Vendor MDM and Location MDM ran independently and their golden records don't cross-reference.
- The **marketing team** knows their golden customer list (from Customer MDM) and their golden product list (from Product MDM) but can't join them — because purchase history tables still reference source system IDs, not golden IDs.

---

## 🟢 The World With Act II: Seven Clean Silos

After all seven domains are mastered independently:

- **Zero** duplicate customers. 2.6M golden customer records.
- **Zero** duplicate SKUs. 12,400 golden product records.
- **Zero** duplicate vendors. 840 golden vendor records.
- **Zero** orphaned assets. 1,089 verified, located, assigned assets.
- **One** authoritative location for every physical place.
- **One** golden employee record per person across all HR systems.
- **One** counterparty record per legal entity, LEI-verified.

The individual domains are reporting correctly. The marketing team's customer emails go to 2.6M unique people (not 3.2M with duplicates). The warehouse manager sees accurate stock counts. The AP team doesn't pay the same supplier twice.

**The CFO's Monday morning question?** Still unanswerable. Because the golden customer record for MAF doesn't link to the golden vendor record for MAF. They are in separate master data stores with no shared identifier.

The silos are cleaner. They are still silos.

---

## 🔧 Technical: The Silo Problem

In a siloed MDM architecture, each domain has its own golden record store:

```
Customer Golden Store:   { GLD-CUST-00890: "MAF Retail (Buyer)", ... }
Vendor Golden Store:     { GLD-VEND-00445: "MAF Logistics (Supplier)", ... }
Counterparty Store:      { GLD-CP-00789: "MAF Treasury (FX)", ... }
```

These three golden records represent the same legal entity. But without cross-domain linkage, no system can join them. A SQL join on `legal_name` would fail (three different name variants). A join on `tax_id` would fail (TRN is in Vendor, not Counterparty). A join on `lei_code` would fail (only Counterparty has LEI in this setup).

The missing layer is a **cross-domain entity resolution table**:

```
cross_domain_links:
  entity_group_id  | domain     | golden_id       | link_type
  ─────────────────────────────────────────────────────────────
  ENT-MAF-001      | customer   | GLD-CUST-00890  | SAME_LEGAL_ENTITY
  ENT-MAF-001      | vendor     | GLD-VEND-00445  | SAME_LEGAL_ENTITY
  ENT-MAF-001      | counterparty | GLD-CP-00789  | SAME_LEGAL_ENTITY
```

Without this table, the silos are clean but blind to each other. Building this table is the work of Act III.

---

# ACT III — THE PARTIAL WEB: Some Domains Talking, Others Left Out

## The First Bridges

In Act III, the MDM team starts building cross-domain links. Not all at once — that would be overwhelming. The first bridges are built between domains that share the most natural foreign keys:

| Bridge | Why First | Foreign Key |
|--------|-----------|-------------|
| Customer ↔ Product | Purchase history — every order links a customer to a product | `customer_golden_id` + `product_golden_id` |
| Employee ↔ Location | Org structure — employees work somewhere | `location_id` on employee record |
| Asset ↔ Location ↔ Employee | Asset ownership triangle | `location_id` + `assigned_to` on asset record |
| Vendor ↔ Product | Approved Vendor List — who supplies what | AVL table linking vendor and product golden IDs |

---

## 🔴 The World Before: When Customer and Product Don't Know Each Other

Priya Sharma — golden customer, trust score 0.87, Gold tier — has a CLV score of AED 8,400.

But that CLV was calculated only from the LOYALTY system. It missed two years of ECOMM purchases because the purchase history table in ECOMM references `ECOMM-00234` (Priya's old source ID) and the CLV model was fed the golden customer IDs, not the source IDs. The join failed silently. The CLV model saw no ECOMM history.

Her real CLV — once all three source records' history is aggregated to her golden ID — is AED 12,000. She's 43% more valuable than the model thought.

The personalisation engine, trained on wrong CLV data, never offered her the Gold-tier exclusive product launches. She starts buying from a competitor.

---

## 🟢 Customer × Product: The Bridge Is Built

AURUM publishes a **source ID resolution table** after each MDM run:

```
source_id_map:
  source_id      | golden_id
  ────────────────────────────────────
  CRM-00101      | GLD-CUST-00101
  ECOMM-00234    | GLD-CUST-00101
  LOYALTY-00089  | GLD-CUST-00101
  SKU-0042       | GLD-PROD-00042
  sku_0042       | GLD-PROD-00042
  SKU0042        | GLD-PROD-00042
```

The purchase history table is re-anchored:

```
Before:
  ECOMM-00234 bought SKU0042 × 2 on 2024-03-20  → not in CLV model

After:
  GLD-CUST-00101 bought GLD-PROD-00042 × 2 on 2024-03-20  → in CLV model ✓
```

Priya's true CLV is now visible. The personalisation engine reclassifies her. She gets the Gold exclusive offer. She stays.

---

## 🔴 The Asset-Location-Employee Triangle Without Bridges

A Dell laptop (AST-0301) is assigned to Lena. Lena just rejoined the company (new golden ID: GLD-EMP-00892). Her old record (EMP-00512) is inactive.

The ITSM system, which manages IT support tickets, has the laptop linked to EMP-00512. Lena raises a support ticket for a hardware issue. The ITSM system looks up the asset — it's assigned to EMP-00512 (inactive). The ticket routing logic says "inactive employee" and misfires the ticket to the IT archive queue instead of the active support queue. The ticket sits unseen for 3 days.

Meanwhile, the laptop's `location_id` still references `LOC-001` (Dubai Mall) — but Lena works from the new Dubai Hills store. The maintenance contractor is dispatched to Dubai Mall. Nobody is there.

---

## 🟢 The Ownership Triangle — Bridges Built

AURUM's cross-domain reanchoring resolves all three foreign keys on the asset record:

```
Asset: GLD-ASSET-0301 (Dell Laptop)
  location_id:    LOC-001 → GLD-LOC-STORE-2A  (Dubai Hills)
  assigned_to:    EMP-00512 → GLD-EMP-00892   (Lena, rehire)
```

The ITSM system consumes the updated golden asset record. Lena's support ticket routes to the correct queue. The contractor is dispatched to the right store. The laptop is fixed the same day.

---

## ⚠️ What Act III Still Leaves Broken

In Act III, the bridges built are:
- ✅ Customer ↔ Product (purchase history)
- ✅ Employee ↔ Location (org structure)
- ✅ Asset ↔ Location ↔ Employee (ownership triangle)
- ✅ Vendor ↔ Product (approved vendor list)

**Left out:**
- ❌ **Counterparty** is still isolated. MAF's three roles (customer, vendor, counterparty) are still three separate golden records with no shared entity group ID. Treasury still can't answer the net exposure question.
- ❌ **Customer ↔ Location** — which customers belong to which store catchment? The loyalty system still routes offers to the nearest *source system* store, not the golden location. Customers near the new Dubai Hills store are still getting Dubai Mall offers.
- ❌ **Vendor ↔ Location** — which vendors supply which stores? The supply chain team still can't see approved vendor lists by store. The new Dubai Hills store opening requires manual vendor qualification because the system can't query "approved vendors for this location."
- ❌ **Employee ↔ Product** — which products can each employee's team see, approve, or purchase? The product approval workflow still uses HRMS email addresses, not golden employee IDs.

The web is growing. But it has gaps. And in enterprise MDM, the gaps are where the money hides.

---

## 🔧 Technical: Cross-Domain Reference Integrity

The core technical problem in Act III is **referential integrity across domain stores**.

When Location MDM runs and merges `LOC-001` and `LOC-045` into `GLD-LOC-0045`, every other domain that has `location_id: LOC-001` in its records is now holding a **stale reference**. The reference is not broken (the old ID still exists in the source ID map) but it is no longer the canonical ID.

AURUM handles this with a **cascading reanchor sweep** after each domain MDM run:

```python
# After Location MDM publishes new golden records:
# 1. Build source_id → golden_id map for Location domain
# 2. Scan all other domain golden records for location_id fields
# 3. Where location_id is a stale source ID → resolve to golden_id
# 4. Publish updated cross-domain records
# 5. Log CROSS_DOMAIN_REANCHOR events in MARK

def reanchor_cross_domain(asset_records, location_id_map):
    for asset in asset_records:
        if asset.location_id in location_id_map:
            old_id = asset.location_id
            asset.golden_location_id = location_id_map[old_id]
            asset.source_location_id = old_id  # retain for audit
            mark.log(CROSS_DOMAIN_REANCHOR, asset_id=asset.id,
                     old_location=old_id,
                     new_location=asset.golden_location_id)
```

This sweep must run in dependency order: Location first (no dependencies), then Asset and Employee (depend on Location), then Purchase History (depends on Customer and Product). Getting the order wrong causes partial updates — some records reanchored, some still stale.

---

# ACT IV — THE GOLDEN WEB: All Seven Domains Talking

## Imagine a World

Imagine a world where when you create a new store, your data estate knows about it within hours — not weeks.

Where employees are automatically provisioned to the store, their assets are linked to the location, their org hierarchy is validated against the location hierarchy, their cost centres are correct, and their AD access is scoped to the right systems — *before* the doors open.

Where the products listed at that store are golden products — one SKU, one price, one barcode — linked to approved golden vendors who have been qualified for that store's supply chain.

Where the customers in that store's catchment area are golden customers — one record per person, with their full purchase history, their correct loyalty tier, their preferred channel — and they receive one personalised opening offer, not three duplicated generic ones.

Where the landlord is a golden counterparty — LEI-verified, sanctions-screened, lease booked in the financial system, IFRS 16 right-of-use asset registered — and the net financial exposure to that counterparty is visible to treasury on day one.

And where every single one of these data relationships — every link, every decision, every survivorship choice, every steward approval — is recorded in a lineage store that can answer any audit question in seconds.

That world exists. AURUM calls it the Golden Web.

---

## 🔴 The World Before: New Store Opening Without MDM

*January 1st. Dubai Hills Mall. Store 2A opens.*

**6:00 AM — The manager can't log in.**
The store manager's AD account was provisioned last night. But her HRMS record still shows the old Dubai Mall store as her location. The POS system validates manager access against HRMS location. Access denied. The IT helpdesk is closed until 8am.

**8:30 AM — The POS won't scan.**
15 of the 340 product SKUs aren't in the store's POS database. They were in the ECOMM catalogue under one SKU format, but the POS system was loaded from ERP, which has a different format. The cashier manually keys prices for those items all day. Three are keyed incorrectly.

**11:00 AM — A customer complains.**
She signed up for the loyalty app last week and selected the Dubai Hills store as her preferred store. But the loyalty system shows her as belonging to the Dubai Mall store because the Dubai Hills location didn't exist in the loyalty system at sign-up time — it was added two days before opening, but the nightly sync hadn't propagated it to the app. She gets a "Welcome to Dubai Mall" push notification while standing in Dubai Hills.

**2:00 PM — The first delivery arrives.**
Three of the eight approved vendors for this store are delivering today. The delivery note references one vendor's trading name; the WMS is looking for the legal name. The GRN (goods receipt note) can't be posted. The stock sits in the loading bay.

**4:00 PM — The CFO asks for the P&L.**
There is no P&L for Store 2A. The location doesn't exist in the financial hierarchy yet. The lease payment was booked to a manual GL entry. The fixed assets (POS terminals, HVAC, server rack) haven't been registered yet — they arrived today. Store 2A's day-one revenue will be manually allocated by finance at month-end.

**End of day — The audit trail.**
The IT team asks: "How many assets were delivered to Store 2A today?" Nobody knows. The CMDB wasn't updated. The FM system has 12 of the 35 assets. The delivery manifest has all 35 but uses the contractor's asset tag format, not the CMDB format.

---

## 🟢 The World With MDM: The Golden Store Opening

*The same store. The same day. With AURUM's Golden Web.*

**Six weeks before opening:**

Location MDM runs. `GLD-LOC-STORE-2A` is created — correct address, correct geocoordinates (200m correction applied), correct parent hierarchy (UAE → Dubai → Dubai Hills → Store 2A). All downstream systems receive the golden location ID within 24 hours. The loyalty app, the POS system, the HR system, the financial hierarchy — all updated.

**Four weeks before opening:**

Employee MDM runs for the 22 new store hires. Three rehires detected and linked. The store manager's dual record (old tech writer role + new store manager role) resolved as a role transition — one golden record, one AD account. All 22 employee records have `location_id: GLD-LOC-STORE-2A`. AD provisioning requests generated for the 4 accounts still pending. POS access scoped correctly.

**Three weeks before opening:**

Asset MDM runs. 35 pre-registered assets with placeholder serial numbers held in `PENDING_DELIVERY` state. Asset-location links set to `GLD-LOC-STORE-2A`. Asset-employee assignments drafted. Insurance certificate pre-generated (pending serial number confirmation).

**Two weeks before opening:**

Product MDM runs for the 340 store SKUs. 5 discontinued products excluded automatically. 12 UOM conflicts resolved (EA primary, KG alt with conversion factor). POS loaded with 335 golden product records — one SKU, one barcode, one price per product. WMS loaded with the same.

Vendor MDM runs for the 8 store suppliers. 6 fully qualified. 2 in 30-day provisional status (pending TRN remediation). Approved Vendor List linked to `GLD-LOC-STORE-2A`. Supply chain team has a single view of which vendors supply this store.

**One week before opening:**

Counterparty MDM runs. Emaar Properties PJSC (the landlord) — 3 source records from LEGAL, TREASURY, and COMPLIANCE — merged into one golden counterparty `GLD-CP-EMAAR`. LEI verified from GLEIF. Lease booked in the financial system against `GLD-CP-EMAAR`. IFRS 16 right-of-use asset registered. Rent payments automated — no more manual GL entries.

Customer catchment assignment: 4,200 loyalty customers in the Dubai Hills catchment area assigned to `GLD-LOC-STORE-2A`. 1,100 source-ID re-anchors applied (post-Customer MDM). 340 first-time store assignments. Opening campaign sent — one email per golden customer.

**Day 1 — January 1st:**

**6:00 AM** — The store manager logs in. AD account is linked to her golden employee record, which is linked to `GLD-LOC-STORE-2A`. POS grants manager access. First time in recent memory that a store opened on time.

**9:00 AM** — The POS scans every product. 335 golden SKUs. One barcode per product. One price.

**11:00 AM** — A loyalty customer gets a push notification: "Welcome to Dubai Hills Mall — your new preferred store. Enjoy 10% off today." She is standing in Dubai Hills. She smiles.

**2:00 PM** — The delivery arrives. The delivery note references the vendor's trading name. The WMS resolves it against the golden vendor record (trading name is an alias on `GLD-VEND-0301`). GRN posted automatically. Stock enters the system. All 35 assets have their placeholder serial numbers replaced by the scanned real serials on delivery — AURUM matches them by asset tag, updates the golden asset records, confirms the insurance certificate.

**4:00 PM** — The CFO runs the P&L. Store 2A exists in the financial hierarchy. Lease is booked. Assets are on the register. Revenue from today's sales posts to the correct location code. It's not a full day's report — it's 7 hours — but it's real, it's clean, and it's there.

**End of day — The audit trail.**
```
MARK query: GET /lineage?location_id=GLD-LOC-STORE-2A
→ location_mastered:         2024-12-01  (6 weeks ago)
→ employees_assigned:        22          (2024-12-15)
→ assets_provisioned:        35          (serial confirmed 2025-01-01 09:14)
→ products_listed:           335         (2024-12-20)
→ vendors_qualified:         8           (6 approved, 2 provisional)
→ counterparty_onboarded:    Emaar       (2024-12-05, LEI verified)
→ customers_assigned:        4,200       (2025-01-01 00:01)
→ day_1_revenue:             AED 47,230  (7 hours, 335 SKUs, 22 staff)
→ day_1_blockers:            0
```

Seven domains. One event. One lineage trail. Zero blockers.

---

## 🔧 Technical: The Orchestrated MDM Platform

### The Dependency Graph

Not all domains can run in any order. AURUM enforces a dependency sequence for the cross-domain Golden Web:

```
Step 1: Location MDM        (no external dependencies — run first)
        │
Step 2: Counterparty MDM    (no external dependencies — can parallel with Location)
        │
Step 3: Vendor MDM          (no external dependencies — can parallel)
        │
Step 4: Employee MDM        (depends on Location — needs golden location IDs)
Step 4: Asset MDM           (depends on Location — needs golden location IDs)
        │
Step 5: Product MDM         (depends on Vendor — AVL needs golden vendor IDs)
        │
Step 6: Customer MDM        (can run anytime, but catchment assignment needs Location)
        │
Step 7: Cross-Domain Sweep  (reanchor all stale foreign keys across all domains)
        │
Step 8: Lineage Validation  (verify all cross-domain links are consistent)
```

### The Cross-Domain Entity Resolution Table

The golden web is held together by one table — the entity group registry:

```sql
CREATE TABLE entity_groups (
    entity_group_id  VARCHAR(64) PRIMARY KEY,  -- "ENT-MAF-001"
    canonical_name   VARCHAR(255),
    canonical_lei    VARCHAR(20),
    canonical_tax_id VARCHAR(50)
);

CREATE TABLE entity_group_members (
    entity_group_id  VARCHAR(64) REFERENCES entity_groups,
    domain           VARCHAR(32),   -- "customer", "vendor", "counterparty"
    golden_id        VARCHAR(64),   -- "GLD-CUST-00890"
    role             VARCHAR(64),   -- "buyer", "supplier", "fx_counterparty"
    link_confirmed_by VARCHAR(128), -- "Nadia"
    link_confirmed_at TIMESTAMP
);
```

With this table, the CFO's Monday morning question is a three-line query:

```sql
SELECT egm.domain, egm.role, egm.golden_id
FROM entity_groups eg
JOIN entity_group_members egm ON eg.entity_group_id = egm.entity_group_id
WHERE eg.canonical_name ILIKE '%Majid Al Futtaim%';
```

Returns three rows: customer (AED 850K AR), vendor (AED 1.5M AP), counterparty (AED 200K MTM). Net: AED -450K.

The CFO has her answer in 4 seconds.

### The Lineage Store

AURUM's MARK stage maintains an append-only lineage log. Every event — every ingestion, every DQ flag, every match decision, every survivorship choice, every steward approval, every publication, every reverse sync — is a record in the lineage store.

```python
@dataclass
class LineageEvent:
    event_id:      str        # UUID
    timestamp:     datetime
    event_type:    str        # INGESTED | MATCHED | GOLDEN_ASSEMBLED | ...
    domain:        str        # "customer", "vendor", ...
    source_id:     str | None # original source record ID
    golden_id:     str | None # golden record ID
    actor:         str        # "AURUM_REFINE" | "Jin (Steward)" | ...
    detail:        dict       # event-specific payload
    cross_domain:  bool       # True if this event crosses domain boundaries
```

For a regulatory audit, the query is:

```python
events = lineage.query(
    golden_id="GLD-CP-EMAAR",
    event_types=["ONBOARDED", "SCREENED", "FIELD_CONFLICT", "HIERARCHY_CORRECTED"],
    date_range=("2018-01-01", "2024-12-31")
)
# Returns: complete provenance for Emaar counterparty since relationship started
```

No manual reconstruction. No spreadsheet archaeology. The answer is always there.

---

# The Numbers: What Each Act of MDM Is Worth

This is not a vendor pitch. These are realistic order-of-magnitude estimates based on the scenarios in this library. Every number is traceable to a specific use case.

| MDM Stage | What Improves | Order of Magnitude Value |
|-----------|--------------|--------------------------|
| **Act I: Single Domain** | Duplicate customer elimination | Reduce marketing waste by 15–25% (duplicate sends, duplicate CLV miscalculation) |
| **Act I: Single Domain** | Duplicate vendor detection | Prevent duplicate payments — typically 0.5–2% of AP spend |
| **Act I: Single Domain** | Asset orphan detection | Reduce ghost assets by 10–20% of fixed asset register value |
| **Act II: All Silos** | Product SKU deduplication | Reduce inventory carrying costs (no split-SKU phantom stock) |
| **Act II: All Silos** | Employee JML | Reduce security incidents from lingering access |
| **Act II: All Silos** | Counterparty LEI validation | Avoid regulatory fines (EMIR, UAE CBUAE) |
| **Act III: Partial Web** | Customer × Product CLV | 10–40% CLV uplift from complete purchase history |
| **Act III: Partial Web** | Asset ownership triangle | ITSM ticket routing accuracy; maintenance contractor dispatch accuracy |
| **Act IV: Golden Web** | New store opening (7 domains) | Day-1 operational readiness; zero IT blockers; complete P&L from day one |
| **Act IV: Golden Web** | Counterparty net exposure | Basel III large exposure compliance; netting-off opportunities |
| **Act IV: Golden Web** | Full audit trail | SAR responses in minutes not days; regulatory examination pass rate |

---

# Epilogue: From Ore to Gold

The name AURUM is not accidental. In metallurgy, gold does not come out of the ground as a shining bar. It comes as ore — mixed with rock, oxidised, unrecognisable for what it is. The journey from ore to hallmarked gold requires five stages: assay the raw material, unearth what is buried, refine away the impurities, unfurl the finished product into the world, and mark it with proof of provenance.

Data follows the same arc.

Your source systems are not wrong. They are ore. They contain real information about real customers, real products, real employees, real places. The information is there. It is just mixed with duplicates and format errors and missing values and conflicting hierarchies and stale foreign keys and placeholder LEIs.

MDM is the refinery.

And like a refinery, MDM works best when it is not a one-time project but a continuous process — running with every new batch of data, surfacing every new DQ issue, maintaining every cross-domain link, recording every steward decision, and getting faster and more accurate over time as the stewardship team learns the patterns.

The Golden Web is not a destination. It is a discipline.

**AURUM** gives you the tools. The use cases in this library give you the patterns. The team — Shazia, Pierre, Arun, Jin, Nadia, Carlos, Lena, Amara, Tariq, Sofia, Inaayah, Alishba, Gaurav, Busi — gives you the expertise.

What you bring is the will to treat your data as the strategic asset it actually is.

---

*Raw data in. Hallmarked golden records out.*

*— Inaayah, Technical Writer, AURUM Project*
*— Raja Shahnawaz Soni, Author & Architect*

---

## References

All scenarios in this document are drawn from the AURUM use-case library:

- [Tier 1 — Single Domain Use Cases](../../use_cases/01_customer/) through [07_counterparty](../../use_cases/07_counterparty/)
- [Tier 2 — Cross-Domain Pairs](../../use_cases/08_cross_domain_pairs/)
- [Tier 3 — Grand Scenario: New Store Opening](../../use_cases/09_grand_scenario/UC-GS01_new_store_opening.md)

The AURUM pipeline that implements all of these patterns is at [github.com/RajaMDM/AURUM](https://github.com/RajaMDM/AURUM).
