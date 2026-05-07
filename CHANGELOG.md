# Changelog

All notable changes to AURUM will be documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/).

---

## [v0.2.0] — 2026-05-07

### The AI-Era MDM Release — Sample Data, Use Cases, Narrative Docs, Global Compliance

This release transforms AURUM from a working pipeline into the **definitive open-source MDM reference repository** — covering all 7 domains end-to-end with realistic data, 41 real-world scenario playbooks, AI-era narrative documentation, and a global data sovereignty compliance guide.

### Added — Sample Data
- **All 7 domains** now have dirty sample data (previously only 4)
- **3,000 total rows** across Customer(600), Product(500), Vendor(500), Asset(400), Employee(400), Location(300), Counterparty(300)
- Expanded geographic coverage: GCC, UK, US, India, Europe — not GCC-only
- All data uses fictional company names — no real organisations referenced

### Added — Use-Case Library (`use_cases/`)
- **41 MDM scenario playbooks** in three tiers:
  - Tier 1: 35 single-domain use cases (5 per domain × 7 domains)
  - Tier 2: 5 cross-domain pair scenarios (2–3 domains interacting)
  - Tier 3: 1 grand scenario — New Store Opening, all 7 domains in one event
- Every playbook: Summary, Business Impact, Scenario Setup, Example Records, AURUM Pipeline Walk-Through, Stewardship Decision Point, Expected Golden Record, CLI Demo Command

### Added — Narrative Documentation (`docs/narratives/`)
- `THE_INTELLIGENT_REFINERY.md` — MDM in the AI era: LLM rule generation, anomaly detection, MCP-native pipeline, agentic stewardship, the 5 questions every CTO should ask
- `THE_MDM_WORLD.md` — 4-act MDM journey: single domain → silos → partial web → full golden web, before/after stories throughout

### Added — Compliance & Legal (`docs/`)
- `DATA_SOVEREIGNTY_AND_COMPLIANCE.md` — AURUM mapped to: UAE PDPL, ADDA (Abu Dhabi), DDA (Dubai), KSA PDPL + NDMO, Qatar PDPL, Bahrain PDPL, GDPR, UK GDPR, CCPA, HIPAA, India DPDP, China PIPL + DSL, Singapore PDPA, Australia Privacy Act, POPIA and more. Official public document links included.
- `DISCLAIMER.md` — all company names and entities are fictional; any resemblance to real organisations is purely coincidental

### Fixed
- CI: demo hardcoded `n=50` rows → full 600-row dataset; `min(200, len(df))` matcher sample
- CI: ASSAY/UNEARTH assertions `==` → `>=` for any data volume
- CI: GitHub Actions Node.js 24 opt-in added
- All real company names → fictional equivalents throughout docs and use cases
- All team member last names removed — first names only
- Version badge, status line, CITATION.cff → v0.2.0

---

## [v0.1.3] — 2026-05-04

### Added
- **`runtimes/api/`** — FastAPI HTTP runtime exposing the pipeline as 6
  endpoints: `GET /` (metadata), `GET /health`, `GET /domains`, `POST /assay`,
  `POST /unearth/{domain}` (all 7 domains), `POST /anomaly`. Multipart CSV
  upload only — server-side file paths are deliberately not accepted to
  avoid path-traversal risk on any deployment beyond localhost. Auto-generated
  OpenAPI docs at `/docs` and ReDoc at `/redoc`.
- **`tests/test_api.py`** — 13 integration tests using Starlette's TestClient
  (no live server needed): meta endpoints, ASSAY against a real CSV,
  UNEARTH for both customer and product domains, 404 on unknown domain,
  case-insensitive domain matching, anomaly detection with bounds
  enforcement, OpenAPI surface verification, plus content-type and
  empty-file rejection paths.
- **`unearth/llm_rules/`** — LLM rule generator. Translates steward prose
  into reviewable Python rules via the Anthropic SDK (tool-use structured
  output, prompt caching on the system prompt). Each generated rule is
  written to `unearth/llm_rules/generated/` as a Python module plus a
  JSON sidecar carrying the original prompt, model, and timestamp — the
  audit trail required for steward replay. Rules are NEVER auto-promoted.
  AST safety guards reject imports, eval/exec/open calls, and bodies
  that don't define a `check(row: dict) -> bool` function.
- **`tests/test_llm_rules.py`** — 11 tests using a fake Anthropic-compatible
  client (no network calls): rule compilation, system-prompt cache_control,
  forced tool_choice, name sanitisation, dangerous-body rejection, import
  rejection, missing-`check` rejection, empty-prose rejection, missing
  API key behaviour, save-to-disk shape, and missing tool_use handling.
- **`runtimes/cli/`** — `python -m runtimes.cli` CLI built on click + rich
  with five commands: `assay` (schema inspection), `unearth <domain>`
  (DQ profiling for any of the 7 domains), `anomaly` (Isolation Forest
  detection), `demo` (end-to-end pipeline), `domains` (list supported
  domains). Every command supports `--json-out` for machine-readable
  output, and `unearth`/`anomaly` carry `--show-issues` / `--show-flagged`
  for output-size control. Versioned at 0.1.3 via `--version`.
- **`unearth/anomaly/`** — Isolation Forest anomaly detector with generic
  per-column feature engineering (length, character composition, null state,
  row-level empty count). Operates on any CSV across all 7 domains; flags
  rows whose feature combinations are unlike the rest of the dataset and
  reports the top three driving features as z-scores. Deterministic via a
  fixed random seed — same input produces the same output for steward audit.
- **`tests/test_anomaly.py`** — 6 tests covering outlier flagging,
  small-dataset tolerance, summary shape, determinism, all-empty column
  exclusion, and `FlaggedRow` serialization.

### Changed
- README Component Status table — UNEARTH ML anomaly detector flips from
  📋 Planned to ✅ Working. The README's "AI/ML actually working" claim
  now lists Isolation Forest alongside RapidFuzz/Jaro-Winkler.

---

## [v0.1.2] — 2026-05-04

### Added
- **All 7 domain profilers ship working.** Previously only Customer was
  implemented; Product, Vendor, Asset, Location, Employee, and Counterparty
  now have production-ready profilers in `unearth/profiler/domain_profiler.py`.
- **Domain-specific DQ rules** per profiler:
  - **Product** — SKU format, barcode (EAN-8/UPC/EAN-13/GTIN-14), UOM whitelist,
    brand/name casing.
  - **Vendor** — tax ID format, country format, legal-vs-trading name identity
    check, self-parent cycle detection.
  - **Asset** — tag format, lifecycle whitelist (active/maintenance/retired/etc.),
    orphan detection (neither located nor assigned).
  - **Location** — latitude/longitude range checks, Null Island (0,0)
    placeholder detection, self-parent cycle detection.
  - **Employee** — email format, hire-date ISO 8601 enforcement, self-manager
    cycle detection, status whitelist.
  - **Counterparty** — LEI format (ISO 17442 — 20 alphanumeric chars),
    role flagging (must be customer or vendor), jurisdiction completeness.
- **Test suite** under `tests/test_profilers.py` — 16 unit tests covering
  rule firing, clean-data acceptance, summary shape, and empty-file
  tolerance for all 7 profilers. CI runs them on every push.
- `tests/conftest.py` — pytest path setup so the suite runs from the repo
  root without requiring an editable install.

### Changed
- README Component Status table updated — UNEARTH stage now shows seven
  ✅ Working profilers instead of one ✅ + six 📋. The "no overpromises"
  pledge stays honest.
- ROADMAP v0.3.0 entry rewritten — per-domain *matchers* remain the next
  investment, since profilers landed early.

### Documentation
- Each profiler carries a docstring listing the columns it expects and the
  rules it enforces — readable as the spec for that domain's DQ baseline.
- **`docs/architecture/ai-strategy.md`** added — defends where AURUM uses
  LLMs (rule authoring, borderline match adjudication, anomaly explanation,
  steward summaries) versus where it deliberately doesn't (matching at
  scale, survivorship, threshold setting, anomaly detection itself).
  Closes the README cross-reference that previously pointed at a planned
  document.

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
