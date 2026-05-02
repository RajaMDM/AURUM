# AURUM

[![CI](https://github.com/RajaMDM/AURUM/actions/workflows/ci.yml/badge.svg)](https://github.com/RajaMDM/AURUM/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)
[![MCP Compatible](https://img.shields.io/badge/MCP-compatible-blueviolet.svg)](runtimes/mcp/)
[![Power Platform](https://img.shields.io/badge/Power%20Platform-companion-742774.svg)](power-platform/)
[![Maintained by Raja Shahnawaz Soni](https://img.shields.io/badge/maintained%20by-Raja%20Shahnawaz%20Soni-navy.svg)](https://linkedin.com/in/raja-shahnawaz/)

> **Raw data in. Hallmarked golden records out.**

AURUM is a vendor-agnostic, AI-augmented Master Data Management reference
implementation. Five stages — named for the journey from raw ore to hallmarked
gold — cover the full MDM lifecycle across 7 domains with working Python, a
Power Platform companion track, and a practitioner certification program.

Not a framework. Not vendor marketing. A working reference you fork, run, and adapt.

---

## The Five Stages

In metallurgy, gold starts as raw ore. It is assayed, unearthed, refined,
unfurled into the world, and hallmarked with proof of provenance. MDM follows
the same arc — and every stage name tells you exactly what happens there.

```
Source Systems
      │
      ▼
┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐
│  ASSAY   │──▶│ UNEARTH  │──▶│  REFINE  │──▶│  UNFURL  │──▶│   MARK   │
│          │   │          │   │          │   │          │   │          │
│ Test the │   │ Surface  │   │ Fuse many│   │ Issue to │   │ Stamp    │
│ raw ore  │   │ what's   │   │ into one │   │ the world│   │ lineage  │
│          │   │ buried   │   │ golden   │   │          │   │& provenance│
│          │   │          │   │ record   │   │          │   │          │
└──────────┘   └──────────┘   └──────────┘   └──────────┘   └──────────┘
                                    │
                            Golden Record Store
```

| # | Stage | Responsibility | AI Layer |
|---|-------|---------------|----------|
| 01 | **ASSAY** | Ingestion · Schema Mapping · Migration | Semantic schema mapper |
| 02 | **UNEARTH** | Profiling · DQ Rules · Anomaly Detection | LLM rule generator · ML anomaly |
| 03 | **REFINE** | Blocking · Matching · Survivorship · Golden Record | ML matcher · AI survivorship |
| 04 | **UNFURL** | Publication · APIs · Subscriptions | Smart consumer routing |
| 05 | **MARK** | Reverse Integration · Lineage · Reconciliation | Lineage inference |

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

## Power Platform Track

AURUM ships a companion Microsoft Power Platform track:
- **Dataverse YAML schemas** — deployable entity definitions for all 7 domains
- **Power Automate flow specs** — stewardship workflows, approval chains, exception routing
- **AI Builder patterns** — form processing, DQ prediction models
- **Copilot Studio** — MDM steward assistant configuration

See [`power-platform/`](power-platform/).

---

## MCP Compatibility

The AURUM pipeline is invocable as an MCP server — works with Claude Code,
Cursor, and any Hermes/Nous-based agentic runtime.

```bash
python runtimes/mcp/server.py
```

---

## Certification Program

| Tier | Focus |
|------|-------|
| **Foundation** | MDM concepts, domain theory, data quality fundamentals |
| **Practitioner** | Hands-on: profiling, matching, survivorship, publication |
| **Architect** | Operating model, AI augmentation, Power Platform integration |

See [`certification/`](certification/).

---

## Author

Built and maintained by **[Raja Shahnawaz Soni](https://linkedin.com/in/raja-shahnawaz/)** —
Enterprise Data Management Practitioner, speaker at Informatica World 2023, and builder of
[The MDM Lab](https://data-alchemist.raja-cloudmdm.workers.dev),
[BrainDrop](https://rajamdm.github.io/braindrop), SYNAPTIQ, QualIQ, and Agents for Good.

> *"Anyone can describe a system. I'd rather hand you a working one and say — here, try it."*

---

## License

MIT © Raja Shahnawaz Soni — see [LICENSE](LICENSE)
