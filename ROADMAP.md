# AURUM Roadmap

This document captures what's planned, what triggers each milestone, and what
practitioners can expect to see when. The README's Component Status table
links here for any item marked 📋.

---

## v0.1.2 — Released

Per-domain depth pulled forward from v0.3.0 — all 7 profilers now ship
working with a full unit-test suite.

**What landed:**
- UNEARTH: Product, Vendor, Asset, Location, Employee, Counterparty
  profilers (each with domain-specific rules)
- 16-test unit suite under `tests/test_profilers.py`
- README Component Status table updated to reflect 7 ✅ working profilers
- Repo ABOUT section completed (description, topics, homepage)

---

## v0.1.1 — Released

The first defensible reference. Architecturally complete pipeline with one
fully-working domain (Customer) end-to-end.

**What landed:**
- All 5 stages scaffolded with correct directory structure
- ASSAY: Schema inspector
- UNEARTH: Customer profiler with format/completeness/consistency rules
- REFINE: Matcher with name-boost floor, transitive cluster builder,
  standardize → validate → survive survivorship pipeline, linked-tuple
  geography to prevent frankenrecords
- MARK: In-memory lineage tracker
- Runtimes: MCP server with 3 working tools
- Power Platform: Customer Dataverse schema
- Demo: End-to-end pipeline with CI assertions
- Trust files: SECURITY, CONTRIBUTING, CODE_OF_CONDUCT, CITATION

---

## v0.2.0 — Working AI + Power Platform breadth

The release that makes the README's AI claims real and the Power Platform
companion track substantive.

### UNEARTH — AI components

- **`unearth/llm_rules/`** — LLM-based DQ rule generator
  - Input: business description in plain English ("phone numbers must be
    UAE-format if country is UAE")
  - Output: executable Python rule attached to the rule engine
  - Backend: Anthropic API (configurable to OpenAI)
- **`unearth/anomaly/`** — ML anomaly detector
  - Isolation Forest from scikit-learn
  - Per-domain feature engineering
  - Outputs flagged records with anomaly scores for steward review

### REFINE — LLM tiebreaker

- For pairs scoring between 0.55 and 0.65 (the borderline zone),
  invoke an LLM with structured output to make the match decision
- Logged separately for steward audit
- Caps usage to avoid LLM cost runaway

### MARK — Reverse integration that actually works

- **`mark/reverse_sync/`** — given a golden record change, compute
  affected downstream consumers and produce an ordered sync plan
- **`mark/reconciliation/`** — detect when a downstream system has
  drifted from the master (scheduled job pattern)

### Power Platform — beyond one schema

- All 7 domains as Dataverse YAML (currently 1)
- 3 Power Automate flow JSON exports:
  - Steward Approval workflow
  - Exception Routing
  - Daily Reconciliation
- AI Builder model definitions (DQ Score Predictor)
- Copilot Studio bot config (MDM Steward Assistant)

### Trigger to start v0.2.0
Either (a) external interest signal — first 5 stars or first issue — or
(b) week of focused build time available. Whichever comes first.

---

## v0.3.0 — Per-domain depth

Profilers landed early in v0.1.2; the remaining v0.3.0 investment is
*matchers* — the harder per-domain problem.

- Domain-specific matchers (Product needs SKU normalization; Vendor needs
  legal entity disambiguation; Asset needs lifecycle-aware matching)
- Domain-specific Dataverse schemas with relationships
- Sample data generators for Vendor, Employee, and Counterparty
  (Customer/Product/Asset/Location already covered)

---

## v0.4.0 — Runtime breadth

- FastAPI HTTP runtime with full OpenAPI docs
- Streamlit UI for steward operations
- Airflow / Prefect / Dagster orchestration
- CLI with click

---

## v1.0.0 — First stable release

Trigger: 100+ stars, at least 3 external contributors with merged PRs,
CI green for 30 consecutive days, all v0.2.0 and v0.3.0 items shipped.

At v1.0.0 the certification program (currently outline only) ships with
real lab content and assessment.

---

## Out of Scope (current)

- Vendor-locked implementations (Informatica, Reltio, Stibo)
- Real production deployment (this is a reference, not a tool)
- Customer-facing UI beyond Streamlit
- Multi-tenancy patterns (single-org reference is the focus)

---

*Maintained by [@RajaMDM](https://github.com/RajaMDM). Open a
[Discussion](../../discussions) to propose roadmap changes.*
