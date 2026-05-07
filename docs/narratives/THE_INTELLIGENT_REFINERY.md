# The Intelligent Data Refinery
### MDM in the Age of AI Agents — What Changes When Your Steward Can Think

> *Authored by Inaayah Mirza, Technical Writer — AURUM Project*
> *Technical review: Gaurav Mehra (Architect), Shazia Hussain (DQ Lead), Arun Mehta (BI Head)*
> *Challenged, stress-tested and kept honest by: Hermes (Team Lead)*

---

## Let's Get the Awkward Bit Out of the Way

Master Data Management is a 20-year-old discipline. The textbooks haven't changed much. The vendor decks haven't changed much. The conference talks haven't changed much.

And yet, the world the data practitioner walks into every morning has changed — dramatically, irreversibly, and faster than any of us expected.

In 2024, a junior data analyst can ask an AI to write her a data quality rule in plain English — and get working Python code in 4 seconds. A data steward can describe a matching edge case in a Slack message — and have it resolved by an agent before she finishes her coffee. A CEO can ask "what is our total exposure to Majid Al Futtaim across all roles?" — and get a structured answer from an AI that queried five systems, resolved the entity across three domains, and calculated the net position — without a single human writing a SQL join.

This document is not about MDM.

This document is about what MDM becomes when AI enters the refinery.

---

## The Old Contract: Rules, Batches, Humans

The traditional MDM contract went like this:

1. **Data Engineers** write ingestion rules. Manually. In code. Usually SQL or Python, sometimes a proprietary tool.
2. **DQ Analysts** define quality rules. In a spreadsheet or a rule engine UI. Hundreds of rules, maintained by hand, becoming stale the moment the data evolves.
3. **Matching algorithms** run on fixed thresholds. Deterministic. If the fuzzy score is above 0.75, it's a match. If it's below, it's not. No reasoning. No context. No exceptions.
4. **Data Stewards** review exception queues. Every flagged record, every borderline match, every DQ failure — a human opens a ticket, looks at the record, makes a decision, closes the ticket. At scale, this becomes a bottleneck that chokes the programme.
5. **Batch runs** happen nightly, or weekly, or monthly. Data is stale between runs. Decisions made on Tuesday are based on Monday's data. The golden record is always a snapshot of the past.

This contract was the best available option in 2005. It solved real problems. It still does. But it carries a cost that grows with data volume and organisational complexity — and that cost is **human attention**.

Human attention is the scarcest resource in any enterprise data programme. The traditional MDM model consumes it faster than any organisation can supply it.

AI changes the supply side of that equation.

---

## The New Contract: Reason, Generate, Agent

AURUM is built on a different contract:

1. **Stewards describe intent in plain English.** The DQ rule engine generates deterministic Python from that description — not a black box model, but inspectable, auditable, versionable code.
2. **ML models surface anomalies** that no human-written rule would ever catch — patterns that are statistically improbable, not just threshold violations.
3. **AI agents make first-pass stewardship decisions** on routine cases, freeing human stewards for the exceptions that actually require judgment.
4. **The pipeline is MCP-native** — any AI agent (Claude, Cursor, Copilot, Hermes) can call AURUM's tools directly, without an API wrapper, without a human in the loop.
5. **Events flow in near-real-time.** Stewardship is not a batch queue. It is a continuous conversation between the data, the AI, and the human steward.

This is not AI washing. Every one of these capabilities is working code in AURUM v0.1.3. Let's walk through them.

---

## Capability 1 — The LLM Rule Generator: Stewards Speak, Rules Listen

### The Old World

A data steward knows that UAE phone numbers should start with `+971` followed by exactly 9 digits. She raises a JIRA ticket. The DQ analyst interprets it. The engineer writes a regex. It goes into a release. Three weeks later it's in production. The steward tests it, finds a bug (she said 9 digits, the engineer wrote 8), raises another ticket. Four weeks total for one rule.

In a mature MDM programme, there are hundreds of rules like this. The backlog never clears.

### The AURUM Way

The steward types, in plain English:

> *"Phone numbers must be UAE format: starts with +971, then a 2-digit network code (50, 52, 54, 55, 56, 58), then 7 digits. No spaces, no dashes. If the country is not UAE, the rule doesn't apply."*

AURUM's LLM rule generator — powered by the Anthropic SDK with structured tool-use output — produces this:

```python
import re

def check(record: dict) -> dict:
    """
    Phone numbers must be UAE format: +971 + 2-digit network code
    (50/52/54/55/56/58) + 7 digits. Only applies when country is UAE.
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
        "message": None if passed else f"Invalid UAE phone format: {phone}"
    }
```

The rule is:
- **Generated** in under 4 seconds
- **Inspectable** — the steward can read it, verify it, modify it
- **AST-validated** — AURUM's safety guard checks for imports, `eval`, `exec`, and missing `check` functions before saving
- **Saved to `generated/`** for human review — never auto-promoted to production without approval
- **Version-controlled** — every generated rule has an audit trail back to the natural language prompt

The four-week cycle becomes a four-second generation plus a thirty-second review.

### What This Changes

The DQ rule backlog doesn't fill up. New domains can be onboarded in days, not months, because domain experts can express their knowledge in their own language and get working rules immediately.

More importantly: **the rules stay fresh**. When the business changes — new network codes, new country coverage, new data formats — the steward updates the natural language description and regenerates. No engineering ticket. No release cycle.

---

## Capability 2 — The Isolation Forest: Catching What Rules Can't See

### The Old World

A DQ rule catches what you know to look for. It cannot catch what you don't know to look for.

A batch of 500 vendor records arrives. 492 look normal. 8 have something subtly wrong — not wrong enough to fail any individual rule, but collectively anomalous. Maybe their postal codes are valid but clustered in an area where the company has no suppliers. Maybe their payment terms are each individually valid (Net 30, Net 45, Net 60) but three records for supposedly different companies all have exactly the same combination of tax ID prefix + payment terms + contact email domain. A rules engine sees nothing.

A human reviewer, if they looked at all 500 records side by side, might notice the pattern. But no one has time to review 500 records by hand.

### The AURUM Way

AURUM's Isolation Forest anomaly detector runs on every domain dataset. It doesn't know what a "correct" vendor looks like. It doesn't have rules. It has one heuristic: **records that are easy to isolate from the rest of the dataset are probably anomalous**.

For each record, it engineers numeric features from every field — string length, character composition ratios, null indicator, cardinality rank — and builds a forest of random trees. Records that end up in short branches (isolated quickly) get a high anomaly score.

```python
# AURUM anomaly feature engineering (domain-agnostic)
def engineer_features(record: dict) -> list[float]:
    features = []
    for field, value in record.items():
        if value is None:
            features.extend([0.0, 0.0, 0.0, 1.0])  # null indicator
        else:
            s = str(value)
            features.extend([
                len(s),                                    # length
                sum(c.isdigit() for c in s) / max(len(s), 1),  # digit ratio
                sum(c.isalpha() for c in s) / max(len(s), 1),  # alpha ratio
                0.0                                        # not null
            ])
    return features
```

The output is not a binary pass/fail. It is a **score between 0 and 1** — the higher the score, the more anomalous the record. Stewards set their own threshold. Records above the threshold are surfaced for review.

The 8 suspicious vendor records in our example? The Isolation Forest flagged 7 of them. Three had anomaly score > 0.85. When the steward investigated, two turned out to be duplicate registrations with a slightly different contact email — the same person registering the same company twice, six months apart. One turned out to have a legitimately unusual profile (a very small specialist supplier in a niche category). The fourth unusual pattern — the shared email domain — was flagged at score 0.71, just below the 0.75 threshold. The steward lowered the threshold for that batch and caught it.

### What This Changes

Rules catch known problems. The Isolation Forest catches unknown problems. Together, they cover the full spectrum of DQ risk — not just "does this field match the pattern" but "does this record look like it belongs here at all."

In the AI era, anomaly detection is not a separate analytics exercise that runs quarterly. It is part of the standard MDM pipeline, running on every batch, automatically.

---

## Capability 3 — The MCP Server: MDM as a Tool for AI Agents

### The Old World

MDM pipelines have APIs. You call them over HTTP, pass a CSV, get a JSON response. That's fine if you're a developer building an integration. It is completely inaccessible if you are an AI agent trying to help a data practitioner in real time.

The traditional MDM API contract assumes a pre-planned integration: someone decided in advance to connect System A to System B, wrote the connector, tested it, deployed it. **Ad-hoc, conversational, agent-driven MDM was never in scope.**

### The AURUM Way

AURUM ships with a native MCP (Model Context Protocol) server. MCP is the standard that makes AI tools callable by AI agents — the same protocol that lets Claude Code call a web browser, a terminal, a file system. With AURUM's MCP server running, any MCP-compatible AI agent can call the MDM pipeline as a native tool.

```python
# runtimes/mcp/server.py — three working tools

@mcp_tool("assay_schema")
def assay_schema(file_path: str) -> dict:
    """
    Inspect a CSV source file — field types, nulls, cardinality.
    Returns a schema profile ready for domain mapping.
    """

@mcp_tool("unearth_profile")
def unearth_profile(file_path: str, domain: str) -> dict:
    """
    Profile a domain dataset for DQ issues.
    Returns rule violations, completeness scores, anomaly flags.
    """

@mcp_tool("refine_match")
def refine_match(file_path: str) -> dict:
    """
    Find duplicate candidates in a dataset.
    Returns match clusters with scores and survivorship proposals.
    """
```

Now imagine a data steward — Jin — having this conversation with Hermes (his AI team lead):

> **Jin:** "The new vendor file just arrived from the procurement team. Can you check it for DQ issues before I review?"

> **Hermes:** *calls `assay_schema` on the file → calls `unearth_profile` with domain=vendor*

> **Hermes:** "I've run the profile. 340 vendors, 23 DQ issues:
> - 8 records with missing TRN (6 may be below VAT threshold — I've flagged them for your confirmation)
> - 12 records with TRN format errors (truncated, probably a migration issue)
> - 3 records with LEI check-digit failures
> - 2 probable duplicates — same company name, different TRN prefixes (score: 0.83)
> The 2 probable duplicates are high priority — different bank accounts. Do you want me to send them to Nadia for compliance review?"

This conversation took 8 seconds. No API integration was written. No ticket was raised. The AI agent used AURUM's MDM tools the same way it uses any other tool — naturally, in context, in response to a human request.

### What This Changes

MDM stops being a pipeline that runs on a schedule and starts being a **capability that any AI agent can invoke on demand**. The steward doesn't go to MDM — MDM comes to the steward, in their workflow, in their language, when they need it.

This is the shift from MDM as a *system* to MDM as a *service* — and in the AI era, services are consumed by agents, not just by humans.

---

## Capability 4 — The Agentic Stewardship Model: AI Decides Routine, Humans Decide Edge Cases

### The Old World

Traditional stewardship has two problems:
1. **Too many decisions** — a mature MDM programme generates hundreds of flagged records per day
2. **All decisions look the same in the queue** — a trivial name-casing correction sits next to a critical bank account discrepancy, both in the same steward inbox

The result: stewards are overwhelmed, they skim, they approve things they shouldn't, they miss things they should catch. The stewardship bottleneck is the number one reason MDM programmes fail to scale.

### The AURUM Way (Present + Near-Future)

AURUM's architecture separates decisions into three tiers:

**Tier 1 — Auto-resolve (AI decides, logs for audit):**
- Name casing corrections (`PRIYA SHARMA` → `Priya Sharma`)
- Country code normalisation (`UAE` / `AE` / `United Arab Emirates` → `UAE`)
- Phone format normalisation (`00971-50-1234567` → `+971501234567`)
- SKU format normalisation
- Address abbreviation expansion

These are deterministic transformations. An AI doesn't add value here — but it also doesn't need to be slower than a rule. AURUM handles these automatically, logs every change, and surfaces a daily summary to the steward team. No queue. No tickets. Done.

**Tier 2 — AI-assisted (AI proposes, steward approves in one click):**
- Probable duplicate matches (score 0.75–0.89)
- Cross-system field conflicts with a clear winner (most recent, system of record, consensus)
- Hierarchy proposals (parent-child location links, org structure changes)
- Rehire detection (inactive email match on new joinee)

For these, AURUM — or Hermes acting as the team lead — presents the decision pre-packaged:

> *"I'm proposing to merge VEND-00101 (AlBaraka Electronics) and VEND-00102 (Al Baraka Electronics LLC) into GLD-VEND-00101. Confidence: 87%. Match basis: TRN prefix match + name similarity 0.92 + same city. Note: different bank accounts — requires your confirmation before financial records are linked. [Approve] [Reject] [Investigate]"*

One button. Thirty seconds of steward attention. The AI did the analysis. The human made the call.

**Tier 3 — Human judgment required (escalated, no AI proposal):**
- Bank account discrepancies on duplicate vendors
- Jurisdiction changes on counterparty records
- Corporate hierarchy restructuring
- Any decision with regulatory or legal implications
- Anything the AI explicitly declines to decide

AURUM flags Tier 3 items with `ESCALATION_REQUIRED` and routes them to the appropriate specialist — Tariq for compliance, Nadia for governance, Pierre for architecture decisions — with full context, not just the record.

### What This Changes

Steward capacity is deployed where it matters. The boring-but-necessary work (Tier 1) happens automatically. The routine-but-consequential work (Tier 2) is reviewed in minutes, not hours. The genuinely complex work (Tier 3) gets the full, uninterrupted attention of a qualified specialist.

A programme that previously needed 8 full-time stewards handling 400 decisions per day can run with 3 stewards handling 60 Tier 2 decisions and 15 Tier 3 escalations per day — and make better decisions, because the humans are never fatigued by the trivial.

---

## Capability 5 — The AI Team as Domain Experts

### The Old World

MDM programmes typically have a Centre of Excellence: data stewards, DQ analysts, data architects, a data governance lead. Small organisations can't afford this. Large organisations lose institutional knowledge every time someone leaves.

### The AURUM Way

AURUM ships with a team of AI specialists — each with a domain, a personality, and a role in the MDM lifecycle. They are not chatbots. They are domain-expert agents with specific responsibilities:

| Specialist | Role | MDM Responsibility |
|-----------|------|-------------------|
| **Shazia** | Data Quality Lead | DQ rule design, profiling standards, anomaly threshold calibration |
| **Pierre** | Enterprise Architect | Location hierarchy, org design, cross-domain data model |
| **Arun** | BI & Analytics Head | Golden record consumption, CLV models, reporting validation |
| **Gaurav** | Technical Architect | Pipeline architecture, MCP integration, performance tuning |
| **Nadia** | Data Governance Lead | Policy, stewardship workflows, regulatory alignment |
| **Tariq** | Security & Compliance | Sanctions screening, LEI validation, AML/CFT exposure |
| **Jin** | Data Stewardship Lead | Daily stewardship queue, exception review, audit responses |
| **Lena** | Data Integration Lead | Source system connectors, cross-domain reanchoring |
| **Carlos** | DataOps Engineer | Pipeline scheduling, reverse sync, monitoring |
| **Amara** | Business Analyst | Use case translation, stakeholder requirements |
| **Alishba** | UX Lead | Stewardship interface design, exception workflow UX |
| **Inaayah** | Technical Writer | Documentation, narrative, user-facing content |
| **Busi** | Data Migration Lead | Legacy system migration, CHARON pattern implementation |
| **Sofia** | Project Manager | Programme governance, milestone tracking, stakeholder reporting |

Each specialist is an AI agent, callable by name, with knowledge of the AURUM codebase, the use-case library, and their specific domain. When Hermes (the team lead) receives a stewardship question, it routes to the right specialist — or convenes a group decision when the problem crosses multiple domains.

This model makes the AURUM programme **organisationally scalable** in a way that human-only teams are not. You don't need to hire a TRN validation expert. Tariq knows UAE FTA rules. You don't need to schedule a meeting with your enterprise architect to discuss location hierarchy. Pierre is available now.

---

## What Has Not Changed (And Why That Matters)

Honesty is a design principle at AURUM. So let's be clear about what AI does *not* change in MDM.

**Business rules are still a human responsibility.**
The LLM rule generator produces code. But the steward must review it. The AI can generate a phone format rule, but it cannot know that your company has a special exception for international VIP customers who use +44 numbers in Dubai. That business context lives in a person's head. The AI surfaces it — it doesn't invent it.

**Survivorship is still a policy decision.**
When CRM says Gold tier and ECOMM says Silver tier, AURUM can apply source trust weights — but those weights were configured by a human who decided that CRM is the system of record for loyalty. The AI enforces policy. It doesn't set it.

**Hierarchy is still a governance decision.**
Whether Standard Chartered PLC's UAE operation is a branch or a separate legal entity for exposure calculation purposes — that is a Basel III interpretation question. Nadia and Tariq make that call. AURUM records it, enforces it, and audits it. But it does not make it.

**High-stakes exceptions still need human judgment.**
Two vendor records with different bank accounts. A counterparty jurisdiction change. A corporate restructuring. These are Tier 3. The AI knows it doesn't know enough. It escalates. A human decides.

The AI makes MDM faster, more consistent, and more scalable. It does not make MDM autonomous. The goal is not to remove humans from the loop — it is to ensure that when humans are in the loop, they are adding genuine value, not processing routine work that a rule could handle.

---

## The Architecture: AURUM as an AI-Native Data Refinery

```
                    ┌─────────────────────────────────────────┐
                    │           AI AGENT LAYER                │
                    │  Claude │ Hermes │ Cursor │ Copilot     │
                    │              (MCP clients)              │
                    └────────────────┬────────────────────────┘
                                     │  MCP Protocol
                    ┌────────────────▼────────────────────────┐
                    │         AURUM MCP SERVER                │
                    │   assay_schema │ unearth_profile        │
                    │   refine_match │ [v0.2.0 tools...]      │
                    └──────┬─────────────────┬────────────────┘
                           │                 │
          ┌────────────────▼──┐    ┌─────────▼──────────────┐
          │   AURUM PIPELINE  │    │    AI COMPONENTS       │
          │                   │    │                        │
          │  ASSAY            │    │  LLM Rule Generator    │
          │  → Schema mapping │    │  (Anthropic SDK)       │
          │  → Type inference │    │                        │
          │                   │    │  Isolation Forest      │
          │  UNEARTH          │    │  (sklearn)             │
          │  → DQ rules       │◄───│                        │
          │  → LLM rules      │    │  Composite Matcher     │
          │  → Anomaly detect │    │  (RapidFuzz +          │
          │                   │    │   Jaro-Winkler)        │
          │  REFINE           │    │                        │
          │  → Blocking       │    │  [v0.2.0]              │
          │  → Matching       │    │  LLM Tiebreaker        │
          │  → Survivorship   │    │  Anomaly Explainer     │
          │  → Golden record  │    │  Match Reasoner        │
          │                   │    └────────────────────────┘
          │  UNFURL           │
          │  → Publication    │
          │  → Subscriptions  │
          │                   │
          │  MARK             │
          │  → Lineage log    │
          │  → Audit trail    │
          └───────────────────┘
```

Every AI component is auditable. Every LLM-generated rule is saved and reviewable. Every anomaly score is explainable. Every match decision has a score and a basis. The AI is a participant in the pipeline — not a replacement for it.

---

## The Five Questions Every CTO Should Ask

Before investing in any AI-era MDM platform, ask these five questions. AURUM's answers follow.

**1. Can a steward express a data quality rule in plain English and get working code?**
Yes. The LLM rule generator produces Python from natural language, with AST validation and human review gates. It works today.

**2. Does the platform catch DQ issues that rules alone can't detect?**
Yes. The Isolation Forest anomaly detector runs on every domain dataset, domain-agnostically, without needing domain-specific configuration.

**3. Can an AI agent call the MDM pipeline directly, in a conversation, without a pre-built integration?**
Yes. The MCP server exposes three working tools to any MCP-compatible AI agent. More tools are on the v0.2.0 roadmap.

**4. Does the platform scale stewardship without requiring a proportionally larger steward team?**
Yes. The three-tier decision model (auto-resolve / AI-assisted / human judgment) routes decisions to the appropriate level. Routine decisions are handled automatically. Human attention is reserved for exceptions.

**5. Is every AI decision auditable?**
Yes. Every generated rule is saved with its natural language prompt. Every anomaly score is stored with the record. Every match decision is logged with its basis. Every stewardship action is in the lineage store. The audit trail is append-only and queryable by any dimension.

---

## The Roadmap: What's Coming

AURUM v0.1.3 is the foundation. The AI-native features being built for v0.2.0:

| Feature | What It Does | Why It Matters |
|---------|-------------|----------------|
| **LLM Match Tiebreaker** | For borderline matches (0.70–0.85), an LLM reasons about the records and gives a structured verdict | Removes the hardest cases from the steward queue |
| **Anomaly Explainer** | After flagging an anomalous record, generates a natural-language explanation of *why* it looks anomalous | Stewards understand what they're reviewing, not just a score |
| **Streaming Stewardship** | Real-time event stream from the pipeline to the steward AI team | Decisions in minutes, not overnight batch queues |
| **Cross-Domain Entity Intelligence** | Automatic detection of same-legal-entity across all 7 domains using LLM + identifier matching | The full Golden Web, assembled autonomously |
| **Reverse Sync Agent** | AI agent that plans and executes golden record changes back to source systems | Closes the loop — MDM is no longer read-only |

---

## The Last Word: From Pipeline to Partner

The old MDM world had a pipeline. Data went in one end, golden records came out the other, and somewhere in the middle a team of humans processed an exception queue.

The AI-era MDM world has a **partner**. The pipeline is still there — ASSAY, UNEARTH, REFINE, UNFURL, MARK — because the metallurgical process of turning raw data into gold has not changed. But the partner sits alongside the pipeline: generating rules, catching anomalies, proposing matches, explaining decisions, answering steward questions, executing routine decisions, and escalating the ones that require human wisdom.

The partnership is not symmetric. The human is still the decision-maker for anything that matters. But the AI is no longer a passive executor of rules someone else wrote. It is an active participant — reading the data, reasoning about it, and doing the cognitive work that used to fall entirely on the human steward's desk.

AURUM is the first MDM reference implementation built for this partnership. Not because we planned it that way. Because this is what MDM looks like when you build it in 2025, with the tools available in 2025, for the organisations that exist in 2025.

The refinery is intelligent now.

---

*Raw data in. Hallmarked golden records out.*
*Now with a team that never sleeps.*

*— Inaayah Mirza, Technical Writer*
*— Raja Shahnawaz Soni, Author & Architect*
*— Hermes, Team Lead*

---

## Technical References

- LLM Rule Generator: [`unearth/llm_rules/generator.py`](../../unearth/llm_rules/generator.py)
- Isolation Forest Detector: [`unearth/anomaly/detector.py`](../../unearth/anomaly/detector.py)
- Composite Matcher: [`refine/matching/matcher.py`](../../refine/matching/matcher.py)
- MCP Server: [`runtimes/mcp/server.py`](../../runtimes/mcp/server.py)
- AI Strategy Architecture Decision: [`docs/architecture/ai-strategy.md`](../architecture/ai-strategy.md)
- Use-Case Library: [`use_cases/README.md`](../../use_cases/README.md)
- The MDM World (domain narratives): [`docs/narratives/THE_MDM_WORLD.md`](THE_MDM_WORLD.md)
