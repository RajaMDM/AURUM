# Changelog

All notable changes to AURUM will be documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/).

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
