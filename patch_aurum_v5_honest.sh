#!/usr/bin/env bash
# =============================================================================
# patch_aurum_v5_honest.sh — Path A: Make the README honest.
# Rewrites README.md, creates ROADMAP.md and CHANGELOG.md.
# Adds an explicit v0.1.1 vs v0.2.0 split so practitioners aren't misled.
# =============================================================================
set -euo pipefail

if [ ! -d ".git" ]; then
  echo "ERROR: run from the AURUM repo root."
  exit 1
fi

echo "==> Backing up to .patch_backup/v5/..."
mkdir -p .patch_backup/v5
cp README.md .patch_backup/v5/README.md.bak

# =============================================================================
# README.md — Honest version
# =============================================================================
echo "==> Writing honest README.md..."
cat > README.md << 'MD_EOF'
# AURUM

[![CI](https://github.com/RajaMDM/AURUM/actions/workflows/ci.yml/badge.svg)](https://github.com/RajaMDM/AURUM/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)
[![MCP Compatible](https://img.shields.io/badge/MCP-compatible-blueviolet.svg)](runtimes/mcp/)
[![Status](https://img.shields.io/badge/status-v0.1.1%20reference-orange.svg)](ROADMAP.md)
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

> Note: Sample data and the `Customer` profiler are fully implemented in v0.1.1.
> Other domains have schema/model definitions; per-domain profilers and
> matchers are on the v0.2.0 roadmap.

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
| Profilers for the other 6 domains | 📋 Planned | Customer is the reference pattern |
| DQ rule engine (standalone) | 🔧 Stub | Rules currently embedded in profilers |
| ML anomaly detector | 📋 Planned | Isolation Forest planned for v0.2.0 |
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
| CLI | 📋 Planned | Directory scaffolded |
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

## AI / ML in v0.1.1 — what's actually there

The repo claims AI augmentation across stages. In v0.1.1 the *working* AI/ML
components are:

- **REFINE classical ML matching** — RapidFuzz token scoring + Jellyfish
  Jaro-Winkler + composite weighting. Deterministic, fast, well-understood.
  Not LLM-based — and that's the right choice for matching at scale.
- **MCP server** — exposes the AURUM pipeline as an MCP-compatible server
  invokable from Claude Code, Cursor, and any Hermes/Nous-based agentic runtime.

LLM-based components (rule generation, anomaly explanation, match tiebreakers)
are designed and scaffolded but **not yet implemented**. They land in v0.2.0.
The architectural choice — where LLMs add value vs. where they add risk in MDM
— is documented in [`docs/architecture/ai-strategy.md`](docs/architecture/ai-strategy.md).
*(Doc itself: 📋 planned — to be written with v0.2.0.)*

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

- Per-domain profilers (Product, Vendor, Asset, Location, Employee, Counterparty)
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
MD_EOF

# =============================================================================
# ROADMAP.md
# =============================================================================
echo "==> Writing ROADMAP.md..."
cat > ROADMAP.md << 'MD_EOF'
# AURUM Roadmap

This document captures what's planned, what triggers each milestone, and what
practitioners can expect to see when. The README's Component Status table
links here for any item marked 📋.

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

Once v0.2.0 ships, the next investment is depth across the other 6 domains.

- Profilers for Product, Vendor, Asset, Location, Employee, Counterparty
- Domain-specific matchers (Product needs SKU normalization; Vendor needs
  legal entity disambiguation; Asset needs lifecycle-aware matching)
- Domain-specific Dataverse schemas with relationships

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
MD_EOF

# =============================================================================
# CHANGELOG.md
# =============================================================================
echo "==> Writing CHANGELOG.md..."
cat > CHANGELOG.md << 'MD_EOF'
# Changelog

All notable changes to AURUM will be documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/).

---

## [v0.1.1] — 2026-05-02

### Changed
- **Survivorship pipeline rewritten** with three-step architecture:
  standardize → validate → survive. Real MDM tools cleanse before
  validating before surviving; v0.1.0 jumped straight to validate.
- **Names** now use independent per-field survivorship (the matcher
  established identity; survivorship picks the cleanest version of each
  attribute independently).
- **Geography** (city, country) now uses linked-tuple survivorship —
  the whole tuple comes from one source. Prevents the "Dubai, UK"
  frankenrecord failure mode where independent field selection produces
  geographically impossible combinations.
- **Trust score reformulated**: 0.6 × completeness + 0.4 × source
  diversity. Single-source records cannot exceed ~0.73 — diversity matters.
- **Matcher re-weighted**: name 0.65, email 0.25, phone 0.10. Added a
  name-boost floor so strong name matches alone can carry a pair.
  Threshold lowered to 0.65 with the boost.
- **Sample data generator** now emits geographically-consistent dirty
  pairs (Dubai always with a UAE variant; London always with a UK variant).
  Format variation is realistic dirt; geographic mismatch was unrealistic.

### Added
- **Standardization layer** (`standardize_name`) reverses known dirt
  patterns before validation: leetspeak (@→a in non-email context),
  trailing punctuation. Pluggable via `standardizer` callable for
  domain-specific rules.
- **Transitive cluster builder** (`build_cluster_ids`) — connected
  components on the match graph. A→B and B→C cluster {A, B, C} even if
  A→C wasn't directly scored above threshold.
- **Demo assertions as CI guards**:
  - `len(matches) > 0`, `len(cluster) >= 2`
  - No `@` characters in golden names (validator regression check)
  - Nameless-record assertion (fails loud if validator/standardizer break)
  - Frankenrecord geography assertion (golden city + country must
    co-exist as a pair in some cluster source)

### Fixed
- v0.1.0 produced a "golden record" called `S@R@H Smith` with a misleading
  trust score of 1.0. Names are now standardized before validation.
- v0.1.0 found zero matches above threshold despite duplicates in the data.
  The matcher reweighting and name-boost floor fix this.
- v0.1.0 trust score measured only attribute fill rate, ignoring source
  diversity. Any random row with all fields filled scored 1.0. Fixed.

### Documentation
- README rewritten with explicit Component Status table — every component
  marked ✅ Working, 🔧 Stub, or 📋 Planned. No more overpromising.
- ROADMAP.md added — captures v0.2.0, v0.3.0, v0.4.0, v1.0.0 milestones
  and triggers.
- CHANGELOG.md added — this file.

---

## [v0.1.0] — 2026-05-02

### Added
- Initial reference implementation across all 5 stages
- 7 domain models (Pydantic)
- Sample data generator (deliberately dirty across 4 domains)
- ASSAY schema inspector
- UNEARTH Customer profiler
- REFINE matcher and survivorship (v1 — superseded in v0.1.1)
- UNFURL publisher stub
- MARK lineage tracker
- MCP server with 3 tools
- Power Platform Customer Dataverse schema
- Certification program outline (3-tier curriculum)
- CI workflow (Python 3.10/3.11/3.12)
- Trust files: SECURITY, CONTRIBUTING, CODE_OF_CONDUCT, CITATION, LICENSE
MD_EOF

echo ""
echo "==> Files written. Verify diff is clean:"
git diff --stat README.md
echo ""
echo "==> Then commit + push:"
echo ""
echo "    git add -A"
echo "    cat > /tmp/aurum_msg.txt << 'EOF'"
echo "    docs: honest README + ROADMAP + CHANGELOG (v0.1.1)"
echo ""
echo "    Replaces overpromising status table with explicit Component Status"
echo "    using three honest tiers: Working, Stub, Planned. Adds ROADMAP.md"
echo "    capturing v0.2.0 commitments (real AI components, reverse integration,"
echo "    Power Platform breadth) and CHANGELOG.md documenting the v0.1.0 to"
echo "    v0.1.1 architectural rewrite."
echo "    EOF"
echo "    git commit -F /tmp/aurum_msg.txt"
echo "    git push"
