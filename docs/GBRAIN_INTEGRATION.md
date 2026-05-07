# AURUM + gbrain — The Memory Layer

> *"MDM gives you the golden record. gbrain gives you the memory of how you got there."*

---

## What Is This?

AURUM is a pipeline — it processes data through 5 stages (ASSAY → UNEARTH → REFINE → UNFURL → MARK) and produces golden records. But pipelines are stateless. Every time a steward makes a decision, every time a merge rule is approved, every time a DQ failure is resolved — that knowledge lives in someone's head, in Slack, or in a ticket that gets closed and forgotten.

**gbrain is AURUM's institutional memory.**

It captures every MDM decision, rule, conflict resolution, and stewardship judgement as a living, searchable, connected knowledge graph. When the next similar case arrives — weeks, months, or a steward rotation later — the answer is already there.

---

## The Architecture

```
         ┌─────────────────────────────────────┐
         │           AURUM Pipeline            │
         │                                     │
         │  ASSAY → UNEARTH → REFINE → UNFURL → MARK
         │                                     │
         │  ↕ read context  ↕ write decisions  │
         └─────────────┬───────────────────────┘
                       │
         ┌─────────────▼───────────────────────┐
         │              gbrain                 │
         │                                     │
         │  🧠 Golden Record Decisions         │
         │  🔗 Cross-Domain Knowledge Graph    │
         │  📋 Stewardship Audit Trail         │
         │  🔍 Semantic Search (vector + FTS)  │
         │  💡 Pattern Detection (dream cycle) │
         └─────────────────────────────────────┘
```

---

## Real Use Cases — AURUM + gbrain in Action

### 1. Steward Decision Memory
**Without gbrain:** Jin resolves a Customer merge conflict. The logic lives in his head.  
**With gbrain:** The decision is written as a brain page — entity, rule applied, confidence, rationale. Next time the same pattern appears, AURUM queries gbrain first.

```bash
# Query before making a merge decision
gbrain query "Zephyr Air customer merge loyalty tier conflict"

# Write the decision after resolution
gbrain put-page decisions/customer-merge-CUST-00142 \
  --body "Merged CUST-00142 into CUST-00089. Rule: highest loyalty tier wins. Confidence: 0.94. Rationale: online channel record had more recent transaction data."
```

---

### 2. Cross-Domain Golden Record Conflicts
**Without gbrain:** The Vendor domain flags Zephyr Air as a duplicate. Customer domain has no idea. They're managed in silos.  
**With gbrain:** Both domains write to the same brain. UC-CP01 (Dual-Role Detection) is surfaced automatically when querying either entity.

```bash
gbrain query "Zephyr Air vendor customer dual role"
# → surfaces UC-CP01 playbook + past decisions + linked entities
```

---

### 3. DQ Rule Lineage
**Without gbrain:** Shazia writes a new phone format validation rule. No one knows why it was written, when, or what it fixed.  
**With gbrain:** The rule, the incident that triggered it, and its outcome are all linked in the graph.

```bash
gbrain query "phone format UAE validation rule origin"
# → surfaces the DQ incident, Shazia's decision, the rule applied, results
```

---

### 4. Stewardship Handover (Zero Knowledge Loss)
**Without gbrain:** Jin takes leave. New steward starts cold.  
**With gbrain:** New steward runs:

```bash
gbrain query "Customer domain open issues and recent decisions"
gbrain graph-query customer-domain --depth 2
# → full context: recent merges, open flags, DQ rules, cross-domain links
```

---

### 5. Compliance Audit Trail
**Without gbrain:** Auditor asks — "Show me every decision made on this entity over the last 6 months."  
**With gbrain:**

```bash
gbrain query "CUST-00142 all decisions and changes"
gbrain graph-query cust-00142 --depth 3
# → full lineage: merges, DQ fixes, rule applications, steward approvals — all timestamped
```

---

## Setup (Already Done ✅)

gbrain is installed and AURUM docs + use cases are already indexed:

```bash
# Check status
gbrain doctor --json

# Query AURUM knowledge
gbrain query "your MDM question here"

# Import new docs after changes
gbrain import ~/Projects/AURUM/docs/ --no-embed
gbrain embed --stale
```

**Current brain state:**
- Engine: PGLite (local, zero-config)
- Pages: 60 (9 docs + 51 use cases)
- Chunks: 208 (vector indexed)
- Embedding model: OpenAI text-embedding-3-large

---

## Cron Jobs (Recommended)

Set these up to keep the brain fresh and compounding:

```bash
# Every 15 min — sync new docs
gbrain sync --repo ~/Projects/AURUM && gbrain embed --stale

# Nightly — dream cycle (pattern detection, memory consolidation)
# See: ~/gbrain/docs/guides/cron-schedule.md
```

To wire these into Hermes cron — just say the word.

---

## The Compounding Effect

This is the key insight:

```
Week 1:   60 pages, 208 chunks, keyword + semantic search
Month 1:  200+ pages, decisions logged, graph links forming
Month 3:  Patterns emerging, dream cycle surfacing non-obvious connections
Month 6:  The brain knows your MDM domain better than any new hire ever could
Year 1:   Institutional MDM intelligence — searchable, auditable, AI-queryable
```

The pipeline processes data. The brain processes knowledge. Together, AURUM becomes a system that **learns**.

---

## Team Responsibilities

| Team Member | gbrain Role |
|-------------|------------|
| **Jin** (Stewardship) | Logs all merge decisions + open flags |
| **Shazia** (DQ Lead) | Logs all DQ rule changes + incident resolutions |
| **Nadia** (Governance) | Logs compliance decisions + policy exceptions |
| **Gaurav** (Tech Architect) | Maintains pipeline ↔ brain integration |
| **Hermes** (AI Lead) | Queries brain before every MDM action, writes after |

---

*AURUM v0.2.0 — gbrain integration layer*  
*Brain engine: PGLite v0.28.6*
