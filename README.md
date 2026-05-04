# AURUM

[![CI](https://github.com/RajaMDM/AURUM/actions/workflows/ci.yml/badge.svg)](https://github.com/RajaMDM/AURUM/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)
[![MCP Compatible](https://img.shields.io/badge/MCP-compatible-blueviolet.svg)](runtimes/mcp/)
[![Status](https://img.shields.io/badge/status-v0.1.3%20reference-orange.svg)](ROADMAP.md)
[![Maintained by Raja Shahnawaz Soni](https://img.shields.io/badge/maintained%20by-Raja%20Shahnawaz%20Soni-navy.svg)](https://linkedin.com/in/raja-shahnawaz/)

> **Raw data in. Hallmarked golden records out.**

AURUM is a vendor-agnostic Master Data Management reference implementation.
Five stages — named for the journey from raw ore to hallmarked gold — cover
the full MDM lifecycle across 7 domains.

**Status: v0.1.1.** This is an active reference build. Some components are
working code, some are scaffolded interfaces, some are planned for v0.2.0.
The [Component Status](#component-status) table tells you exactly what's
what — no overpromises. See [ROADMAP.md](ROADMAP.md) for v0.2.0 commitments.

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

> Note: All 7 domain profilers ship working in v0.1.2. Sample data covers
> Customer, Product, Asset, and Location end-to-end. Domain-specific matchers
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
| LLM rule generator | 📋 Planned | Anthropic API integration planned for v0.2.0 |

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
| FastAPI HTTP runtime | 📋 Planned | v0.2.0 |
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
