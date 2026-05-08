# AURUM

[![CI](https://github.com/RajaMDM/AURUM/actions/workflows/ci.yml/badge.svg)](https://github.com/RajaMDM/AURUM/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)
[![MCP Compatible](https://img.shields.io/badge/MCP-compatible-blueviolet.svg)](runtimes/mcp/)
[![Status](https://img.shields.io/badge/status-v0.2.0%20reference-blue.svg)](ROADMAP.md)
[![Maintained by Raja Shahnawaz Soni](https://img.shields.io/badge/maintained%20by-Raja%20Shahnawaz%20Soni-navy.svg)](https://linkedin.com/in/raja-shahnawaz/)

> **Raw data in. Hallmarked golden records out.**

| | |
|---|---|
| 📊 **[Diagrams](https://github.com/RajaMDM/AURUM/blob/main/docs/diagrams/AURUM_DIAGRAMS.md)** | Pipeline · Decision model · gbrain memory · Dream cycle |
| ❓ **[FAQ](https://github.com/RajaMDM/AURUM/blob/main/docs/AURUM_FAQ.md)** | Storage · Enterprise deployment · Air-gapped · Compliance |
| 🧠 **[gbrain Integration](https://github.com/RajaMDM/AURUM/blob/main/docs/GBRAIN_INTEGRATION.md)** | Knowledge graph · Stewardship memory · Nightly dream cycle |

AURUM is a vendor-agnostic Master Data Management reference implementation.
Five stages — named for the journey from raw ore to hallmarked gold — cover
the full MDM lifecycle across 7 domains.

**Status: v0.2.0.** This is an active reference build. Some components are
working code, some are scaffolded interfaces, some are planned for v0.2.0.
The [Component Status](#component-status) table tells you exactly what's
what — no overpromises. See [ROADMAP.md](ROADMAP.md) for v0.2.0 commitments.

---

## Why AURUM?

Traditional MDM programmes share a common shape: a vendor, an SI, a long delivery timeline, and knowledge that walks out the door when the consultants do. AURUM was built because that pattern keeps repeating.

| | Traditional MDM | AURUM |
|---|---|---|
| **Licence** | Annual vendor fee | Free (MIT) |
| **Time to value** | 12–24 months | Days |
| **DQ rule delivery** | Weeks of dev cycles | Seconds (LLM-generated) |
| **Institutional knowledge** | Lives in people | Compounds in the graph |
| **Cross-domain visibility** | Siloed by domain | 7 domains, unified mastering |

**The Knowledge Problem**
![Knowledge That Disappears vs Knowledge That Compounds](https://github.com/RajaMDM/AURUM/blob/main/docs/diagrams/images/c01_knowledge_problem.png?raw=true)

**Time to Ship a DQ Rule**
![6 weeks vs seconds](https://github.com/RajaMDM/AURUM/blob/main/docs/diagrams/images/c02_dq_rule_time.png?raw=true)

**The Invisible Entity Problem**
![Siloed MDM vs Cross-Domain Mastering](https://github.com/RajaMDM/AURUM/blob/main/docs/diagrams/images/c03_invisible_entity.png?raw=true)

**What You're Actually Buying**
![Traditional MDM Cost vs AURUM](https://github.com/RajaMDM/AURUM/blob/main/docs/diagrams/images/c04_what_you_buy.png?raw=true)

---

## Diagrams

Visual walkthroughs of the pipeline, decision model, and knowledge graph layer — all render natively on GitHub:

📊 **[docs/diagrams/AURUM_DIAGRAMS.md](docs/diagrams/AURUM_DIAGRAMS.md)**

Includes: AURUM 5-stage pipeline · Three-tier stewardship model · gbrain memory layer · Nightly dream cycle · Knowledge compounding curve

❓ **[docs/AURUM_FAQ.md](docs/AURUM_FAQ.md)**

Common questions answered in plain English: Where is data stored? · Enterprise deployment options · Air-gapped setup · Does data go to OpenAI? · Is it production-ready? · What does gbrain add?

---

## The Five Stages

In metallurgy, gold starts as raw ore. It is assayed, unearthed, refined,
unfurled into the world, and hallmarked with proof of provenance. MDM follows
the same arc — and every stage name tells you what happens there.

```
Source Systems
      │
      ▼
┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐
│  ASSAY   │──▶│ UNEARTH  │──▶│  REFINE  │──▶│  UNFURL  │──▶│   MARK   │
│          │   │          │   │          │   │          │   │          │
│ Test the │   │ Surface  │   │ Fuse many│   │ Issue to │   │ Stamp    │
│ raw ore  │   │ what's   │   │ into one │   │ the world│   │ lineage  │
│          │   │ buried   │   │ golden   │   │          │   │ &        │
│          │   │          │   │ record   │   │          │   │ provenance│
└──────────┘   └──────────┘   └──────────┘   └──────────┘   └──────────┘
                                    │
                            Golden Record Store
```

| # | Stage | Responsibility |
|---|-------|---------------|
| 01 | **ASSAY** | Ingestion · Schema Mapping · Migration |
| 02 | **UNEARTH** | Profiling · DQ Rules · Anomaly Detection |
| 03 | **REFINE** | Blocking · Matching · Survivorship · Golden Record |
| 04 | **UNFURL** | Publication · APIs · Subscriptions |
| 05 | **MARK** | Reverse Integration · Lineage · Reconciliation |

---

## Domains

| Domain | Core Mastering Challenge |
|--------|--------------------------|
| **Customer** | Identity resolution across channels |
| **Product** | Variant explosion, UOM conflicts, hierarchy |
| **Vendor** | Legal entity vs trading entity, group vs subsidiary |
| **Asset** | Lifecycle state, location drift, maintenance lineage |
| **Location** | Hierarchy conflicts, geocoding drift |
| **Employee** | Org hierarchy changes, multi-role assignments |
| **Counterparty** | Dual role (vendor + customer), legal entity identifiers |

> Note: All 7 domain profilers ship working in v0.2.0. Sample data covers
> all 7 domains end-to-end (600–300 rows each, deliberately dirty). Domain-specific matchers
> (SKU normalization, legal-entity disambiguation, lifecycle-aware matching)
> remain on the v0.3.0 roadmap.

---

## Component Status

Three statuses, no fudge:
- ✅ **Working** — runs end-to-end, tested, demoable
- 🔧 **Stub** — interface exists, full logic deferred
- 📋 **Planned** — directory exists, work scheduled (see [ROADMAP.md](ROADMAP.md))

### ASSAY — Stage 01

| Component | Status | Notes |
|-----------|--------|-------|
| Schema inspector | ✅ Working | Field profiling, type inference, null/cardinality stats |
| CSV connector | ✅ Working | Via pandas, used by demo |
| Other source connectors (REST, DB, flat file) | 📋 Planned | Directory scaffolded |
| Migration cookbook (CHARON pattern) | 📋 Planned | Documented in stage-overview, code pending |

### UNEARTH — Stage 02

| Component | Status | Notes |
|-----------|--------|-------|
| Customer profiler | ✅ Working | Completeness, format, consistency rules |
| Product profiler | ✅ Working | SKU, barcode (EAN/UPC/GTIN), UOM whitelist, brand/name casing |
| Vendor profiler | ✅ Working | Tax ID, country, legal-vs-trading name, self-parent |
| Asset profiler | ✅ Working | Tag format, lifecycle whitelist, orphan detection |
| Location profiler | ✅ Working | Lat/lon range, Null Island detector, self-parent |
| Employee profiler | ✅ Working | Email, hire-date ISO format, self-manager, status whitelist |
| Counterparty profiler | ✅ Working | LEI (ISO 17442), role flagging, jurisdiction |
| DQ rule engine (standalone) | 🔧 Stub | Rules currently embedded in profilers |
| ML anomaly detector | ✅ Working | Isolation Forest with generic per-column feature engineering |
| LLM rule generator | ✅ Working | Anthropic SDK + tool-use schema + AST safety guards; rules saved for steward review, never auto-promoted |

### REFINE — Stage 03

| Component | Status | Notes |
|-----------|--------|-------|
| Matcher (RapidFuzz + Jaro-Winkler + token + name-boost) | ✅ Working | Composite scoring with name-boost floor |
| Transitive cluster builder | ✅ Working | Connected components on the match graph |
| Survivorship engine | ✅ Working | Standardize → validate → survive pipeline |
| Linked-tuple geography survivorship | ✅ Working | Prevents (Dubai, UK) frankenrecords |
| Golden record assembly + trust scoring | ✅ Working | 0.6 × completeness + 0.4 × source diversity |
| Blocking engine (LSH / sorted-neighbourhood) | 🔧 Stub | Naive O(n²) used inline for the demo |
| LLM tiebreaker for borderline matches | 📋 Planned | v0.2.0 |

### UNFURL — Stage 04

| Component | Status | Notes |
|-----------|--------|-------|
| Publisher interface | 🔧 Stub | Defines registry pattern; HTTP push not yet wired |
| FastAPI publication layer | 📋 Planned | v0.2.0 |
| Subscription / consumer routing | 📋 Planned | v0.2.0 |

### MARK — Stage 05

| Component | Status | Notes |
|-----------|--------|-------|
| Lineage event tracker | ✅ Working | In-memory log per record (production: persistent store) |
| Reverse sync engine | 📋 Planned | v0.2.0 — golden-record-change → downstream sync plan |
| Reconciliation | 📋 Planned | v0.2.0 — detect downstream drift from master |

### Runtimes

| Component | Status | Notes |
|-----------|--------|-------|
| MCP server | ✅ Working | 3 tools: `assay_schema`, `unearth_profile`, `refine_match` |
| CLI (click + rich) | ✅ Working | 5 commands: `assay`, `unearth`, `anomaly`, `demo`, `domains` |
| FastAPI HTTP runtime | ✅ Working | 6 endpoints, multipart CSV upload, OpenAPI/ReDoc docs |
| Streamlit UI | 📋 Planned | v0.2.0 |
| Airflow / Prefect orchestration | 📋 Planned | Stubs only |

### Power Platform Companion Track

| Component | Status | Notes |
|-----------|--------|-------|
| Customer Dataverse schema (YAML) | ✅ Working | Deployable via PAC CLI |
| Other 6 domain schemas | 📋 Planned | v0.2.0 |
| Power Automate flow JSON exports | 📋 Planned | v0.2.0 — Steward Approval, Exception Routing, Daily Reconciliation |
| AI Builder model definitions | 📋 Planned | v0.2.0 — DQ Score Predictor |
| Copilot Studio bot config | 📋 Planned | v0.2.0 — MDM Steward Assistant |

### Certification Program

| Component | Status | Notes |
|-----------|--------|-------|
| Curriculum overview (Foundation → Practitioner → Architect) | ✅ Written | 3-tier outline in `certification/README.md` |
| Module content + labs | 📋 Planned | Lab directory exists, content pending |

### Demo

| Component | Status | Notes |
|-----------|--------|-------|
| End-to-end pipeline demo | ✅ Working | All 5 stages run with assertions; CI-verified |

---

## AI / ML in v0.1.3 — what's actually there

The repo claims AI augmentation across stages. In v0.1.3 the *working* AI/ML
components are:

- **REFINE classical ML matching** — RapidFuzz token scoring + Jellyfish
  Jaro-Winkler + composite weighting. Deterministic, fast, well-understood.
  Not LLM-based — and that's the right choice for matching at scale.
- **UNEARTH Isolation Forest anomaly detector** — flags rows whose feature
  combinations are unlike the rest of the dataset. Generic per-column
  feature engineering (length, character composition, null state) so it
  works across all 7 domains without per-domain tuning. Deterministic.
- **UNEARTH LLM rule generator** — translates steward prose ("phone numbers
  must be UAE-format if country is UAE") into deterministic Python rules
  via the Anthropic SDK with tool-use structured output. Saves to a
  `generated/` directory for human review; never auto-promotes. AST
  safety guards reject imports, eval/exec, and missing `check` functions.
- **MCP server** — exposes the AURUM pipeline as an MCP-compatible server
  invokable from Claude Code, Cursor, and any Hermes/Nous-based agentic runtime.

LLM-based components (rule generation, anomaly explanation, match tiebreakers)
are designed and scaffolded but **not yet implemented**. They land in v0.2.0.
The architectural choice — where LLMs add value vs. where they add risk in MDM
— is documented in [`docs/architecture/ai-strategy.md`](docs/architecture/ai-strategy.md).

---

## Quickstart

```bash
git clone https://github.com/RajaMDM/AURUM.git
cd AURUM
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python shared/sample_data/generate_all.py
python demo/end_to_end_demo.py
```

The demo runs ASSAY → UNEARTH → REFINE → UNFURL → MARK end-to-end with
assertions for cluster integrity, frankenrecord detection, and trust scoring.

### CLI usage

```bash
python -m runtimes.cli --help
python -m runtimes.cli assay shared/sample_data/output/customers_dirty.csv
python -m runtimes.cli unearth customer shared/sample_data/output/customers_dirty.csv
python -m runtimes.cli anomaly shared/sample_data/output/customers_dirty.csv --domain customer
python -m runtimes.cli demo
```

Every CLI command supports `--json-out` for machine-readable output.

### HTTP API

```bash
uvicorn runtimes.api.main:app --reload --port 8000
# OpenAPI docs:  http://localhost:8000/docs
# ReDoc:         http://localhost:8000/redoc

# Examples
curl -F file=@shared/sample_data/output/customers_dirty.csv http://localhost:8000/assay
curl -F file=@shared/sample_data/output/customers_dirty.csv http://localhost:8000/unearth/customer
curl -F file=@shared/sample_data/output/customers_dirty.csv "http://localhost:8000/anomaly?domain=customer"
```

---

## Repository Structure

```
AURUM/
├── shared/              # Domain models · Sample data · Utilities
├── assay/               # Stage 01: Ingestion, schema mapping, migration
├── unearth/             # Stage 02: Profiling, DQ, anomaly detection
├── refine/              # Stage 03: Matching, mastering, golden record
├── unfurl/              # Stage 04: Publication, APIs, subscriptions
├── mark/                # Stage 05: Reverse integration, lineage
├── runtimes/            # CLI · FastAPI · MCP · Streamlit · Orchestration
├── power-platform/      # Dataverse schemas · Power Automate · AI Builder
├── certification/       # Foundation → Practitioner → Architect
├── docs/                # Architecture · Methodology · Roles & Agents
└── demo/                # End-to-end pipeline walkthrough
```

---

## MCP Compatibility

The AURUM pipeline is invocable as an MCP server with three working tools:

```bash
python runtimes/mcp/server.py
```

| Tool | Purpose |
|------|---------|
| `assay_schema` | Inspect a CSV source file — field types, nulls, cardinality |
| `unearth_profile` | Profile a customer CSV for DQ issues |
| `refine_match` | Find duplicate candidates in a customer dataset |

Compatible with Claude Code, Cursor, Hermes/Nous, and any MCP-compliant runtime.

---

## Use-Case Library

The [`use_cases/`](use_cases/) directory contains **41 real-world MDM scenario playbooks** across all 7 domains — organised in three tiers: single-domain, cross-domain pairs, and a grand scenario where all 7 domains interact.

| Tier | Use Cases | Description |
|------|-----------|-------------|
| [Tier 1 — Single Domain](use_cases/) | 35 | 5 scenarios per domain |
| [Tier 2 — Cross-Domain Pairs](use_cases/08_cross_domain_pairs/) | 5 | 2–3 domains talking to each other |
| [Tier 3 — Grand Scenario](use_cases/09_grand_scenario/) | 1 | All 7 domains in one real-world event |

| Domain | Use Cases |
|--------|-----------|
| [Customer](use_cases/01_customer/) | Identity resolution, cross-channel merge, DQ failures, golden record conflicts, lineage audit |
| [Product](use_cases/02_product/) | SKU deduplication, UOM conflicts, variant explosion, barcode DQ, price conflicts |
| [Vendor](use_cases/03_vendor/) | Legal vs trading entity, group/subsidiary hierarchy, tax ID DQ, duplicate detection, vendor-customer crossover |
| [Asset](use_cases/04_asset/) | Lifecycle state conflicts, orphaned assets, location drift, serial number dedup, maintenance lineage |
| [Location](use_cases/05_location/) | Hierarchy conflicts, geocoding drift, store/warehouse duplicates, address standardisation, parent-child resolution |
| [Employee](use_cases/06_employee/) | Multi-system identity merge, org hierarchy changes, multi-role assignments, leaver/rehire detection, cost centre realignment |
| [Counterparty](use_cases/07_counterparty/) | Dual-role detection, LEI validation, legal entity dedup, jurisdiction mismatch, relationship lineage |

→ **[Browse all 41 use cases](use_cases/README.md)**

---

## Narratives & Deep Dives

| Document | What It Is |
|----------|-----------|
| [The Intelligent Refinery](docs/narratives/THE_INTELLIGENT_REFINERY.md) | **Start here.** MDM in the AI era — LLM rule generation, agentic stewardship, MCP-native pipeline, the 5 questions every CTO should ask |
| [Imagine a World](docs/narratives/THE_MDM_WORLD.md) | The 4-act MDM journey — single domain → all domains → cross-domain → full golden web, with before/after stories for every scenario |
| [How We Build AURUM](docs/HOW_WE_BUILD.md) | The AI stack behind this project — Hermes, BMAD, gstack, Claude Code, Telegram. Running an enterprise MDM project from a phone. |
| [Data Sovereignty & Compliance](docs/DATA_SOVEREIGNTY_AND_COMPLIANCE.md) | How AURUM aligns with data laws across the GCC (UAE PDPL, ADDA, DDA, KSA PDPL, Qatar PDPL) and globally (GDPR, CCPA, DPDP, PIPL, POPIA and more) |
| [Disclaimer](docs/DISCLAIMER.md) | All company names, entities and scenarios in this repo are entirely fictional. Any resemblance to real organisations is purely coincidental. |

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). High-priority contributions for v0.2.0:

- Domain-specific matchers (Product SKU normalization, Vendor legal-entity
  disambiguation, Asset lifecycle-aware matching)
- LLM rule generator for UNEARTH
- ML anomaly detector for UNEARTH
- Reverse sync engine for MARK
- Power Automate flow exports
- Real Power Apps (model-driven) screenshots

---

## Author

Built and maintained by **[Raja Shahnawaz Soni](https://linkedin.com/in/raja-shahnawaz/)** —
Enterprise Data Management Practitioner, speaker at Informatica World 2023, and
builder of [The MDM Lab](https://data-alchemist.raja-cloudmdm.workers.dev),
[BrainDrop](https://rajamdm.github.io/braindrop), SYNAPTIQ, QualIQ, and Agents for Good.

> *"Anyone can describe a system. I'd rather hand you a working one and say — here, try it."*

---

## License

MIT © Raja Shahnawaz Soni — see [LICENSE](LICENSE)
