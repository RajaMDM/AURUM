# LinkedIn Article — Long Form (v4 — with snippets)
# "I Rebuilt My MDM Practice From Scratch Using AI. Here's What I Learned."
# Raja Shahnawaz Soni
# Target: 2,500 words | LinkedIn Article format
# Status: Ready for Raja's review

---

**I Rebuilt My MDM Practice From Scratch Using AI. Here's What I Learned.**

---

Twenty years ago, I walked into my first Master Data Management project.

Vendor platform. Cost more per year than some clients' entire IT budgets. Team of twelve. Governance committee. Steering group. A project plan already six months stale before the first record was touched.

Eighteen months later, we had a golden record. For the customer domain.

**One domain. Eighteen months. Twelve people.**

I've spent two decades watching that story repeat — different industries, different geographies, different vendor logos on the slides. The shape of the problem barely moves. And neither does the shape of the solution.

This year I decided to rebuild the whole thing from scratch. By myself. In my spare time. Using AI.

What I built is called AURUM. Open source, MIT licensed. But this article isn't really about AURUM. It's about what I *learned* doing it — about MDM, about AI, and about the gap between how we've always done this and how it could actually be done.

---

## The problem is not the software

Let me be direct: MDM programmes fail because of human attention cost. Not technology.

Every MDM programme runs on the same fuel — skilled people doing careful, repetitive work. Engineers writing ingestion rules by hand. DQ analysts maintaining hundreds of checks in spreadsheets. Stewards processing exception queues that grow faster than they can be cleared. Matching thresholds that were set in 2018 and never touched because nobody wants to own what happens when they change them.

At small scale, this is manageable. At enterprise scale, it chokes.

The discipline is sound. The approach is not.

Here's what a typical week in a mature MDM stewardship team actually looks like:

```
Monday morning stewardship queue:
  ├── 847 records flagged for review
  ├── 312 probable duplicate pairs
  ├── 203 DQ rule failures
  ├── 89 cross-system field conflicts
  └── 243 records with missing mandatory fields
  
Team capacity: 2 stewards × 6 hours = ~100 reviewed decisions/day
Queue growth rate: ~200 new items/day

Result: queue doubles every week.
By Friday: 1,200+ unreviewed items.
By month end: team stops looking.
```

MDM doesn't need better software. It needs a different relationship between human attention and mechanical work. In 2025, for the first time, the tools exist to redesign that relationship.

---

## What a steward used to spend four weeks on now takes four seconds

Consider the DQ rule lifecycle. A steward knows something about the data — say, that UAE phone numbers must start with `+971`, followed by a two-digit network code (50, 52, 54, 55, 56, 58), followed by seven digits.

**The old process:**

She raises a ticket. The DQ analyst interprets it. The engineer writes the code. It goes into a sprint. It arrives in production three to four weeks later. She tests it. Finds a bug — she said 9 digits total after the country code, the engineer wrote 8. Another ticket. Another sprint. Six weeks total for one rule. By now the data has evolved.

**The new process:**

She types exactly what she knows, in plain English:

```
"Phone numbers must be UAE format: starts with +971,
then a 2-digit network code (50, 52, 54, 55, 56, 58),
then 7 digits. No spaces or dashes.
Only applies when country field indicates UAE."
```

An AI generates this — in four seconds:

```python
import re

def check(record: dict) -> dict:
    """UAE phone format validation.
    Only applies when country is UAE / AE / United Arab Emirates.
    """
    country_variants = {"UAE", "AE", "United Arab Emirates"}
    if record.get("country") not in country_variants:
        return {"passed": True, "rule": "phone_uae_format", "skipped": True}

    phone = record.get("phone", "")
    pattern = r"^\+971(50|52|54|55|56|58)\d{7}$"
    passed = bool(re.match(pattern, phone))

    return {
        "passed": passed,
        "rule": "phone_uae_format",
        "field": "phone",
        "value": phone,
        "message": None if passed else f"Invalid UAE phone: {phone}"
    }
```

Not a black box. Not a model output that nobody can audit. Actual Python — she can read it, verify it, modify it. It goes through a human review gate before production. If it's right, it ships in thirty seconds. If it's wrong, she corrects the description and it regenerates.

Multiply that across hundreds of rules, seven domains, multiple source systems. The bandwidth difference is not incremental. It is structural.

---

## The stewardship bottleneck — and how to break it

The exception queue is where MDM programmes quietly die.

The problem isn't that stewards are bad at their jobs. The problem is routing — every decision, regardless of complexity, goes through the same human channel. A trivial name-casing correction sits in the same queue as a probable fraud case. Both get the same amount of attention, which means neither gets the right amount.

Here's what the data actually looks like coming in from a real source system migration:

```
# customers_dirty.csv — 600 rows, deliberately dirty
# Sample of what AURUM's UNEARTH stage surfaces:

source_id   | name          | email                        | phone          | issue
CRM-00101   | Priya Sharma  | priya.sharma@company.com     | +971501234567  | ✓ clean
ECOMM-00234 | PRIYA SHARMA  | PRIYA.SHARMA@company.com     | 00971501234567 | email casing, phone format
LOYALTY-089 | priya sharma  | priyasharma@company.com      |                | email variant, phone missing
ERP-00445   | P. Sharma     | p.sharma@company.com         | +971 50 123    | name truncated, phone spaces
PORTAL-0012 | Priya Sharmä  | priya.sharma@company.com     | +971501234567  | diacritic in name

# These are five records for one real person.
# Without MDM: she's counted as five customers.
# Her CLV is split five ways. Her loyalty tier exists in one record only.
# Your churn model thinks four of them haven't purchased in 90 days.
```

AURUM runs these through a three-tier decision model:

```
TIER 1 — Auto-resolve (no human needed):
  ✓ email.lower()          → normalised silently, logged
  ✓ phone normalise        → 00971501234567 → +971501234567, logged
  ✓ name.strip()           → trailing spaces removed, logged
  ✓ diacritic removal      → "Sharmä" → "Sharma", logged

TIER 2 — AI proposes, steward approves in one click:
  → Probable match: CRM-00101 ↔ ECOMM-00234 ↔ LOYALTY-089 ↔ ERP-00445
    Score: 0.94 | Basis: name similarity 0.97, email domain match, phone match
    Proposal: MERGE → GLD-CUST-00101
    Risk note: LOYALTY email differs slightly — steward should confirm
    [Approve ✓]  [Reject ✗]  [Investigate 🔍]

TIER 3 — Human judgment only (escalated, no AI proposal):
  ⚠ ERP-00445 has a different billing address (Sharjah vs Dubai on CRM)
    Could be a legitimate second address, or a data entry error.
    Routed to: Jin (Data Stewardship Lead)
    Context: all purchase history, all address fields, map view
```

One human decision for Tier 3. Thirty seconds for Tier 2. Zero time for Tier 1.

After the merge, this is what the golden record looks like:

```python
{
  "golden_id":     "GLD-CUST-00101",
  "first_name":    "Priya",
  "last_name":     "Sharma",
  "email":         "priya.sharma@company.com",   # CRM/ECOMM consensus
  "phone":         "+971501234567",               # normalised from ECOMM
  "loyalty_tier":  "Gold",                        # LOYALTY — system of record
  "trust_score":   0.91,
  "cluster_size":  5,
  "source_ids":    ["CRM-00101", "ECOMM-00234", "LOYALTY-089",
                    "ERP-00445", "PORTAL-0012"],
  "is_golden":     True
}
```

Priya goes from five phantom identities to one trusted golden record. Her real CLV is now visible. Her loyalty tier flows correctly. Your churn model works.

---

## Seven domains — and what happens when they don't talk to each other

Here's what vendor demos never show you: the real value of MDM isn't one clean domain. It's what happens when all your domains know each other.

A golden customer record that doesn't link to golden products is a deduped contact list. A golden vendor record that doesn't link to the products it supplies is a cleaned AP extract. An employee record that doesn't know which location that person works at is a tidy HRMS export.

The power is in the web.

I'll show you the failure mode first. This is what I've seen in nearly every enterprise MDM programme I've worked on:

```
# After Customer MDM + Product MDM run independently:

purchase_history table (before cross-domain reanchoring):
  purchase_id | customer_id  | sku       | qty | date
  PO-10001    | CRM-00101    | SKU-0042  |  1  | 2024-01-15   ← old source ID
  PO-10002    | ECOMM-00234  | SKU0042   |  2  | 2024-03-20   ← old source ID, old SKU format
  PO-10003    | LOYALTY-089  | sku_0042  |  1  | 2024-06-10   ← old source ID, old SKU format

# The CLV model was fed golden customer IDs.
# The join failed silently.
# Priya's ECOMM and LOYALTY purchases: invisible to the CLV model.
# Her calculated CLV: AED 8,400.   ← wrong
# Her real CLV: AED 12,000.        ← 43% higher
# She never gets the Gold exclusive offer.
# She starts buying from a competitor.
```

After cross-domain reanchoring — publishing a source ID resolution table post-MDM:

```
# source_id_map (published after each MDM run):
  CRM-00101    → GLD-CUST-00101
  ECOMM-00234  → GLD-CUST-00101
  LOYALTY-089  → GLD-CUST-00101
  SKU-0042     → GLD-PROD-00042
  SKU0042      → GLD-PROD-00042
  sku_0042     → GLD-PROD-00042

# purchase_history (after reanchoring):
  PO-10001  | GLD-CUST-00101 | GLD-PROD-00042 | 1 | 2024-01-15  ✓
  PO-10002  | GLD-CUST-00101 | GLD-PROD-00042 | 2 | 2024-03-20  ✓
  PO-10003  | GLD-CUST-00101 | GLD-PROD-00042 | 1 | 2024-06-10  ✓

# Total: 4 units. One customer. One product. Correct CLV. Correct offer.
```

And the CFO's question that nobody could answer before MDM:

```
# "What is our total exposure to Apex Group across all roles?"

# Before cross-domain entity resolution: three separate records, no link.
  CRM:       MAF Retail (customer)    → AED 850K receivable
  ERP:       MAF Logistics (vendor)   → AED 1.5M payable
  Treasury:  MAF Treasury (FX fwd)    → AED 200K MTM gain

# After cross-domain entity resolution (same TRN, same LEI):
  entity_group: ENT-APEX-001
  ├── GLD-CUST-00890  (customer)      → AED +850K  AR
  ├── GLD-VEND-00445  (vendor)        → AED -1.5M  AP
  └── GLD-CP-00789    (counterparty)  → AED +200K  MTM
                                      ─────────────────
                              NET:    AED -450K  payable

# Query time: 4 seconds.
# Previously: 3 days to compile manually. Probably wrong.
```

I documented forty-one scenarios like this in the AURUM use-case library. Single-domain problems. Cross-domain failures. And one grand scenario — opening a new retail store — where all seven domains must cascade correctly from a single business event, in dependency order, before Day 1.

---

## How I'm running this — and why the specific tools don't matter

I want to be honest about how AURUM gets built, because there's a lesson in the *pattern* that's worth more than any specific tool recommendation.

My workflow, in plain terms:

I send a message from my phone. Something like:

```
"The CI is failing. Demo hardcoded to 50 rows,
 dataset is now 3,000. Fix it, bump to v0.2.0,
 cut the release."
```

Within the hour, back on my phone:

```
✅ Demo fixed — now uses full 600-row dataset
✅ matcher sample_size: min(200, len(df)) — guarantees matches
✅ Assertions: >= instead of == (any volume works now)
✅ Version bumped: README, CHANGELOG, CITATION.cff → v0.2.0
✅ Git tag v0.2.0 pushed
✅ GitHub release created — now marked Latest
✅ CI: all 5 jobs green (Python 3.10 / 3.11 / 3.12)

Release: github.com/RajaMDM/AURUM/releases/tag/v0.2.0
```

No laptop. No IDE. No context switching. No meetings.

Behind that: an AI agent runtime with persistent memory, a set of specialist agents scoped to specific domains (DQ, governance, compliance, architecture, documentation), a library of engineering workflow patterns, and an AI execution layer that can read a codebase, patch files, run tests, manage git, and cut releases.

Now here's what matters: **none of those specific tools are the point.**

The pattern is:

```
Pattern: AI-Augmented Development
  ├── Persistent context layer
  │     → remembers every decision, every constraint, every convention
  │     → picks up where you left off, every session
  │
  ├── Specialist agent layer
  │     → scoped expertise per domain (DQ, governance, security, writing)
  │     → not general-purpose chatbots — focused, consistent, accountable
  │
  ├── Workflow pattern layer
  │     → architecture review before building
  │     → code review before committing
  │     → QA pass before shipping
  │     → enforced consistently, not remembered manually
  │
  ├── Execution layer
  │     → writes files, runs terminals, calls git, patches code
  │     → the mechanical work, done at machine speed
  │
  └── Human interface
        → whatever your organisation already uses and approves
        → Slack, Teams, email, a web UI — the pattern doesn't care
```

The specific tools I use are the ones that work for me, on my hardware, with my infosec constraints. They're open source. But this exact pattern runs equally well with enterprise-grade, vendor-supported, SOC 2 compliant alternatives. GitHub Copilot instead of my coding AI. Microsoft Copilot Studio instead of my agent runtime. Teams instead of my messaging platform. Azure OpenAI instead of any public API.

**If your organisation's infosec team has approved it — use it.** The pattern transfers. The specific implementation is yours to choose.

What matters is that you have:
- An AI layer that remembers context across sessions (not a stateless chatbot)
- Specialists scoped to specific domains and responsibilities
- Structured workflow patterns that enforce consistent practices
- A human in the loop for every decision that matters
- An audit trail for everything the AI does

If you're in a regulated environment with strict data residency requirements, run everything on-premise. If your enterprise has a sanctioned AI platform, use that. The shape of the solution doesn't depend on the shape of the tools.

---

## What the lineage looks like at the end

Here's the part I find most compelling — and the part that matters most for compliance.

Every regulator, every auditor, every internal governance committee eventually asks the same question: *"Can you prove your data is accurate, lawfully processed, and traceable?"*

This is what AURUM's lineage store returns for a single golden record:

```
GET /lineage?golden_id=GLD-CUST-00101

{
  "golden_id": "GLD-CUST-00101",
  "events": [
    {"ts": "2025-01-01T09:12:01", "type": "INGESTED",
     "actor": "ASSAY", "detail": "CRM-00101 → 11 fields mapped"},

    {"ts": "2025-01-01T09:12:01", "type": "INGESTED",
     "actor": "ASSAY", "detail": "ECOMM-00234 → 11 fields mapped"},

    {"ts": "2025-01-01T09:12:02", "type": "DQ_FLAG",
     "actor": "UNEARTH", "detail": "email casing on ECOMM-00234"},

    {"ts": "2025-01-01T09:12:02", "type": "MATCHED",
     "actor": "REFINE", "detail": "CRM-00101 ↔ ECOMM-00234, score=0.98"},

    {"ts": "2025-01-01T09:12:03", "type": "GOLDEN_ASSEMBLED",
     "actor": "REFINE", "detail": "trust=0.91, cluster=5 records"},

    {"ts": "2025-01-01T09:14:30", "type": "STEWARD_APPROVED",
     "actor": "Jin", "detail": "Tier 2 merge confirmed"},

    {"ts": "2025-01-01T09:14:31", "type": "PUBLISHED",
     "actor": "UNFURL", "detail": "pushed to CRM, ECOMM, LOYALTY"}
  ],
  "sources_contributing": ["CRM-00101", "ECOMM-00234",
                           "LOYALTY-089", "ERP-00445", "PORTAL-0012"],
  "published_to": ["CRM", "ECOMM", "LOYALTY"],
  "last_updated": "2025-01-01T09:14:31"
}
```

Every ingestion. Every DQ flag. Every match decision. Every steward approval. Every publication. Append-only. Timestamped. Attributed.

For a Subject Access Request under GDPR or UAE PDPL: seconds, not days.
For an audit: a query, not a reconstruction.
For a data erasure request: a cascade, not a manual hunt across six systems.

This is what regulatory compliance looks like when MDM is built correctly from the start.

---

## What I've actually learned

Twenty years of MDM taught me what the problems are.

This year taught me that most of the constraints I'd accepted as *fixed* are actually just the cost of the old toolset.

The four-week DQ rule cycle is not inevitable. It's a consequence of a sequential handoff. Remove the handoff, the cycle collapses.

The stewardship bottleneck is not inevitable. It's a consequence of routing all decisions through the same channel. Route by tier, the bottleneck disappears.

The single-domain silo is not inevitable. It's a consequence of MDM programmes that never planned for cross-domain linkage. Build the entity registry from day one and the silos become a web.

The eighteen-month golden record is not inevitable. It is a symptom of a programme designed around the constraints of 2005.

None of this means MDM is easy. The business rules are still hard. The survivorship decisions are still consequential. The regulatory compliance is still non-negotiable. The judgment calls at Tier 3 are still irreplaceable.

But the *mechanical* work — the rules, the profiling, the match candidates, the documentation, the routine stewardship decisions — is now compressible in a way it has never been before.

The refinery can be intelligent. The question is whether you're willing to redesign it.

---

## AURUM

Everything described in this article is implemented in AURUM — fully working, open source, MIT licensed.

Five pipeline stages. Seven domains. Three runtimes: CLI, HTTP API, and an MCP server so any AI agent can call the MDM pipeline as a native tool. Forty-one use-case playbooks. A global data sovereignty compliance guide with official document links for every jurisdiction. A narrative on MDM in the AI era. And a disclaimer: all company names are fictional.

It is not a product. It is a reference — a working example of what I believe MDM should look like, built the way I believe it should be built, documented the way I wish every MDM programme was documented.

If you find something useful in it, use it. If you disagree with something, I'd genuinely like to know.

**→ github.com/RajaMDM/AURUM**

---

*Twenty years in enterprise data — financial services, retail, public sector, technology. I build things rather than theorise about them. Working on MDM, data governance, or AI-augmented data management? My DMs are open.*

---

**#MasterDataManagement #DataGovernance #DataQuality #AI #AgenticAI #OpenSource #DataEngineering #MDM #DigitalTransformation #EnterpriseData #BuildInPublic #DataStrategy**

---
> Version: v4 — with snippets
> Word count: ~2,600
> Format: LinkedIn Article (Write article, not Start a post)
> Snippet count: 9 code/data blocks woven through the narrative
> Tip: GitHub link in first comment, not article body
> Images: AURUM pipeline ASCII diagram from README works perfectly as a screenshot
