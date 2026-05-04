# AURUM-PP — Technical Layout

A Microsoft Power Platform instantiation of the AURUM master data management reference architecture. AURUM-PP demonstrates that the same five-stage MDM pattern (ASSAY → UNEARTH → REFINE → UNFURL → MARK) and the same matching logic can run on Dataverse + Power Apps + Power Automate — with the matching engine itself imported from the public AURUM Python repository at runtime, not reimplemented.

---

## 1. Project context

### What AURUM is

AURUM (`github.com/RajaMDM/AURUM`) is an open-source Python reference implementation of a five-stage master data management architecture. It defines the stages, names them, gives each its own package (`assay/`, `unearth/`, `refine/`, `unfurl/`, `mark/`), and ships a working matcher and survivorship engine. Each `__init__.py` carries a one-line statement of stage purpose:

- **ASSAY** — "Stage 01: Ingestion, Schema Mapping, Migration. Test the raw ore before processing."
- **UNEARTH** — "Stage 02: Profiling, DQ Rules, Anomaly Detection. Surface what is buried inside the data."
- **REFINE** — "Stage 03: Blocking, Matching, Survivorship, Golden Record. Fuse many records into one trusted golden record."
- **UNFURL** — "Stage 04: Publication, APIs, Subscriptions. Issue the golden record to the world."
- **MARK** — "Stage 05: Reverse Integration, Lineage, Reconciliation. Stamp provenance. Track everything."

AURUM is platform-agnostic by intent: it makes architectural claims about MDM that should hold regardless of where they run.

### What AURUM-PP is

AURUM-PP is the Power Platform realization of that architecture, living as a subfolder of the AURUM repository at `power-platform/`. The two are parent-and-child rather than siblings: AURUM is the umbrella architecture; AURUM-PP is one platform-specific implementation of it. Future implementations on other stacks (Databricks, Informatica, Snowflake) would sit alongside `power-platform/` as additional subfolders, not as separate repositories.

### The mechanical lineage

The strongest defense of "this is genuinely the AURUM architecture, not a Power Platform thing that uses similar words" is a code dependency. AURUM-PP imports the matcher directly from the public AURUM Python tree:

```python
# scripts/load_sample_data.py:70-74
AURUM_REPO_PATH = Path.home() / "Projects" / "AURUM"
sys.path.insert(0, str(AURUM_REPO_PATH))

from refine.matching.matcher import (
    score_pair as _aurum_score_pair,
    ...
)
```

There is no vendored copy. There is no Python re-port. The composite confidence score computed for every demo record is the output of `refine.matching.matcher.score_pair()` running unmodified, against records shaped by AURUM-PP's data model. The matcher integration was first wired in at AURUM commit `78223b6` (recorded in `CHANGELOG.md`); the script captures the live HEAD via `git rev-parse` at run time and writes it into the lineage doc, so any drift is auditable.

For a student audience, the "why this matters" is straightforward: anyone can put MDM concepts on a slide deck. The architecture only counts if it survives a re-implementation. AURUM-PP doesn't re-implement — it imports. That is the proof that the architecture is real.

For a work audience, the same point lands as a procurement and risk argument: the matcher's behavior in AURUM-PP is governed by the public AURUM repository's tests, not by Power Platform-specific logic that nobody else reviews. If the matcher needs to change, you change one file in one repository; both implementations track.

---

## 2. Five-stage AURUM architecture mapped to Power Platform

| AURUM stage | Stage purpose (per `~/Projects/AURUM/<stage>/__init__.py`) | AURUM-PP realization | Concrete artifact | Status |
|---|---|---|---|---|
| **ASSAY** | Ingestion, schema mapping, migration; test the raw ore | `aurum_assay_profile` Dataverse table holds per-field profile output (one row per run × source × field) | `dataverse-schemas/05_aurum_assay_profile.yaml` | Schema deployed, 8 sample rows. |
| **UNEARTH** | Profiling, DQ rules, anomaly detection | Three per-source staging tables hold raw extracts with original "dirt" preserved. Each uses a source-native primary attribute (CRM = full-name display, ECOMM = email, LOYALTY = member number) | `dataverse-schemas/02..04` | Deployed. Hero records loaded. |
| **REFINE** | Blocking, matching, survivorship, golden record | Public AURUM matcher imported at runtime; composite scores written to staging as `aurum_match_confidence`. Two of three Power Automate flows live (auto-approve, steward review). | `scripts/load_sample_data.py:73`; Flow 1 + Flow 2 in `make.powerautomate.com` | Partial — Flow 3 deferred. |
| **UNFURL** | Publication, APIs, subscriptions; issue the golden record to the world | `aurum_customer` canonical table is the publish target. Power Automate flows write into it after match resolution. Flow 3 (manual create-row promotion) deferred. | `dataverse-schemas/01_aurum_customer_canonical.yaml`; `aurum_customer.aurum_is_golden` | Schema deployed; canonical population partial pending Flow 3. |
| **MARK** | Reverse integration, lineage, reconciliation; stamp provenance | Phase 4 deliberately leans on Dataverse's built-in audit log rather than building a custom `aurum_mark_lineage_event` table. Every flow run's row update is captured automatically with actor, timestamp, before/after values. | Dataverse system audit (`audit` entity); per-table `is_audit_enabled: true` set in every YAML | Deployed via platform default. Custom MARK table deferred. |

**On the `aurum_assay_profile` naming convention.** AURUM-PP names its profile-output table `aurum_assay_profile` rather than `aurum_unearth_profile` because in this implementation "assay" is read as a verb — the act of assessing the data — rather than the AURUM stage-01 label. The output of an assay is a profile. Renaming would be a cosmetic change with breakage cost (every script, doc, and view referencing the name) for no architectural improvement. The convention is documented here.

---

## 3. Deployed components inventory

### 3.1 Dataverse schema — five tables

All five tables were deployed via `scripts/deploy_table.py` (909 lines), reading YAML specifications and POSTing through the Dataverse Web API. The deploy was driven by `dataverse-schemas/01..05_*.yaml` and authenticated via MSAL device-code flow (`scripts/auth.py`). The deploy approach was chosen after PAC CLI 2.6.4 hit an unconditional `System.NullReferenceException` inside its OS-broker init on macOS .NET 10 — full failure analysis in `DEFENSE_BRIEF.md` 2026-05-02 entry.

Eleven Dataverse Web API quirks were captured during the deploy and saved to memory (`project_aurum_pp_dataverse_quirks.md`) — boolean shape asymmetries between entity-level and attribute-level, the `IsPrimaryName` triumvirate Dataverse silently requires for entity creation, calc-field XAML deferral, auto-companion columns, the YAML-vs-script-vs-env drift pattern named "Quirk 10". These are not in this document but are referenced where they bite.

| Logical name | Display name | AURUM stage(s) | Primary name attribute | Sample records | Notable |
|---|---|---|---|---:|---|
| `aurum_customer` | Customer (Golden Record) | UNFURL output | `aurum_full_name` | **30** | Has activities + notes; canonical of three staging sources. Lookup target for staging's `aurum_canonical_customer`. |
| `aurum_crm_customer` | CRM Customer (Staging) | UNEARTH | `aurum_full_name_display` (calc field, deferred to maker UI per Quirk 3) | **23** | Source-native primary is the calculated full-name display. |
| `aurum_ecomm_customer` | E-Commerce Customer (Staging) | UNEARTH | `aurum_email_raw` | **20** | Email is the natural source primary; abbreviated names common (`S. Johnson`). |
| `aurum_loyalty_customer` | Loyalty Customer (Staging) | UNEARTH | `aurum_loyalty_member_number` | **15** | Names stored in legacy `LAST, FIRST MIDDLE` ALL-CAPS format; `_parsed` columns hold normalized output. |
| `aurum_assay_profile` | ASSAY Profile Result | ASSAY | `aurum_field_name` | **8** | Per-field profiling output. Eight sample rows demonstrate the shape; production runs would emit ~24 rows per profiling pass (8 fields × 3 staging tables). |

Counts are verified against `scripts/load_sample_data.py:1697-1709` (filler counts: 26 canonicals, 17 CRM, 17 ECOMM, 12 LOYALTY, 8 assay) plus the five hero patterns producing the additional records. Total: **96 rows**.

The single instance of a calculated field anywhere in the schema — `aurum_crm_customer.aurum_full_name_display` — was deferred to manual maker UI creation because Dataverse's Web API requires calc columns' formula as compiled XAML, and synthesizing that programmatically for one column was not worth the R&D investment. A trigger to revisit the XAML synthesis tooling is documented in `ROADMAP.md`.

### 3.2 Sample data

Ninety-six demo records were inserted by `scripts/load_sample_data.py` (~2200 lines). Five hero patterns drive the demonstration narrative:

- **Priya Krishnamurthy** — three-source person with formatting drift (CRM ALL-CAPS, ECOMM clean, LOYALTY legacy comma format). Purpose: show that REFINE's effectiveness depends on UNEARTH's case-folding. The CRM record's composite is `0.51` — below the matcher's `0.55` candidate filter — and is manually linked in the demo. The matcher would not surface it; UNEARTH normalization would lift it. This is the inter-stage dependency made visible. Verified: `docs/demo_records_aurum_lineage.md:28-34`.
- **Mohammed Al-Rashid** — borderline-band match. CRM staging shows `M. Alrashid` (Dubai, different email, no hyphen); canonical has the full name (Abu Dhabi). Phone identical. Composite computed by the public AURUM matcher: **`0.6002`** (`docs/demo_records_aurum_lineage.md:88`). Mohammed sits between the candidate-filter floor (0.55) and the auto-match threshold (0.65) — exactly the band where human judgment is required. Used as Flow 2's verification subject.
- **Sarah Chen** — multi-brand. Same person appears in CRM as a B2B buyer (work email, work address, VIP segment) and in ECOMM as a personal consumer (gmail, home address). CRM composite `1.0000`; ECOMM composite `0.8500` (the boost-floor mechanism activates because `name_score = 1.0` exceeds the 0.90 boost threshold). Used as Flow 1's verification subject.
- **Aisha Mubarak** — conflicting sources for the linked-tuple pattern. CRM and LOYALTY both produce composite `1.0000`. Address fields diverge across sources, but the matcher does not score addresses — addresses are pure UNFURL/survivorship concern. Demonstrates the deliberate stage separation: REFINE answers "are these the same entity"; UNFURL answers "which source's facts survive."
- **New prospect cluster** — four unmatched staging records (Hassan Bin Saeed CRM, Joana Reyes CRM, Lukas Weber ECOMM, Maria L Santos LOYALTY) used as Flow 3 test subjects. All have composite below `0.55` (no canonical link); steward-initiated promotion creates new canonical rows.

The matcher's composite score is computed by:

```
weighted    = name_score * 0.65 + email_score * 0.25 + phone_score * 0.10
boost_floor = name_score * 0.85   if name_score >= 0.90 else 0.0
composite   = max(weighted, boost_floor)
```

Source: `~/Projects/AURUM/refine/matching/matcher.py:81-86`. Phone normalization is `digits-only, last 9 characters, equality compare` (`matcher.py:77-79`). Email is full equality only — no fuzzy partial credit at the canonical-vs-canonical level beyond `_safe_fuzz × 0.3` for non-equal pairs (line 75).

#### The matcher hallucination catch (Day 2 morning)

This is a teaching moment worth surfacing. An earlier draft of `load_sample_data.py` arrived at composite scores by composing imagined components — a "phone-cluster bonus" of 0.25, a "region-similarity factor", and so on — none of which exist in the actual matcher. The catch came when verifying the hero records' confidence values against the public AURUM source. The fix was structural: every demo record's composite is now computed by calling `_aurum_score_pair(canon_rec, stage_rec)` directly (`load_sample_data.py:660`), and the lineage document is regenerated on every script run with the per-pair breakdown emitted by the matcher itself. The arithmetic stops being something the script invents and starts being something the script reports.

### 3.3 Model-driven app — AURUM Steward Workbench

Status: **published, On**. Five entity pages (one per Dataverse table). The sitemap was hand-authored as XML (`model-driven-app/sitemap/aurum_steward_workbench_sitemap.xml`) after the maker UI's sitemap designer failed to expose group-create and group-move operations during the build session.

Three custom system views were built — one `Pending Steward Review` view per staging table. All three share the same shape:

| Aspect | Configuration |
|---|---|
| Filter | `aurum_processing_status eq 5` |
| Sort | `aurum_match_confidence` ascending — lowest-confidence (most ambiguous) records surface first, so the steward exercises judgment where it matters most |
| Source-specific value-indicator column | CRM: `aurum_lifetime_value` (LTV) · ECOMM: total spend · LOYALTY: `aurum_loyalty_tier` |

Filter verified in `docs/phase3_views_specification.md:75` (FetchXML snippet). LOYALTY uses the `_parsed` name columns because legacy data is stored in `LAST, FIRST MIDDLE` ALL-CAPS form; the parsed columns hold normalized output.

**Steward queue contents at time of verification — queried 2026-05-04 via Dataverse Web API (`aurum_processing_status eq 5`, ordered by `aurum_match_confidence asc`):**

CRM — 4 records on `aurum_crm_customer`:

| Source ID | Name (raw) | Match confidence | Match method |
|---|---|---:|---|
| `CRM-00042` | PRIYA KRISHNAMURTHY | 0.51 | FUZZY_BORDERLINE (3) |
| `CRM-00219` | M. Alrashid | 0.60 | FUZZY_BORDERLINE (3) |
| `CRM-20000` | Andrea Cruz | 0.71 | FUZZY_BORDERLINE (3) |
| `CRM-20004` | Tao Wong | 0.71 | FUZZY_BORDERLINE (3) |

ECOMM — 2 records on `aurum_ecomm_customer`:

| Source ID | Name (raw) | Match confidence | Match method |
|---|---|---:|---|
| `ECOMM-20000` | Anjali Bhatt | 0.69 | FUZZY_BORDERLINE (3) |
| `ECOMM-20007` | Wei Li | 0.69 | FUZZY_BORDERLINE (3) |

LOYALTY — 3 records on `aurum_loyalty_customer` (legacy ALL-CAPS source form shown; parsed name in parentheses):

| Member number | Name (legacy / parsed) | Match confidence | Match method |
|---|---|---:|---|
| `VLP-455168` | BIN AHMED, YUSUF (Yusuf Bin Ahmed) | 0.69 | FUZZY_BORDERLINE (3) |
| `VLP-251716` | PETROV, MARCO (Marco Petrov) | 0.71 | FUZZY_BORDERLINE (3) |
| `VLP-527940` | VILLANUEVA, ANDREA (Andrea Villanueva) | 0.79 | FUZZY_BORDERLINE (3) |

**What the queue tells the demo audience.** Nine borderline-band records, none auto-approved, all surfaced via the matcher's FUZZY_BORDERLINE classification. Confidence values cluster in the 0.51–0.79 band — exactly the territory between the candidate filter (0.55) and the auto-match threshold (0.65) plus the upper-borderline strip up to ~0.85. Mohammed (0.60, CRM-00219) is the canonical Flow 2 test subject. Priya (0.51, CRM-00042) is below the matcher's candidate filter — she shows in the queue because the demo manually set her to STEWARD_REVIEW to illustrate the inter-stage UNEARTH dependency (per `docs/demo_records_aurum_lineage.md`'s Priya hero pattern).

Three honest gaps:

- **Forms are auto-generated.** Dataverse's default form layout does not foreground `aurum_match_confidence` or lineage fields. Phase 5 polish replaces them with the per-tab layouts spec'd in `docs/phase3_forms_specification.md`.
- **Sitemap is per-table, not stage-grouped.** The original design called for ASSAY / UNEARTH / REFINE / UNFURL navigation groups; the maker UI bug forced the per-table fallback. Reorganization is a Phase 5 cleanup item.
- **Emoji in titles deferred** because rendering across browser/OS combinations was uncertain.

> [SCREENSHOT: AURUM Steward Workbench sitemap]
> [SCREENSHOT: Pending Steward Review (CRM) view with Mohammed visible]

### 3.4 Power Automate flows

Two flows live, one deferred.

#### Flow 1 — `AURUM | REFINE | Auto-Approve High-Confidence Match (CRM)`

- **Trigger**: Dataverse "When a row is added, modified or deleted" on `aurum_crm_customer`. Change type: Added or Modified. Scope: Organization. Selected columns: `aurum_match_confidence, aurum_processing_status, aurum_canonical_customer`.
- **Filter** (OData): `aurum_match_confidence ge 0.85 and aurum_processing_status eq 3`.
- **Condition**: `aurum_canonical_customer is not null` (defensive; terminate otherwise).
- **Action**: Update staging row, set `aurum_processing_status = 4` (`SURVIVED`).
- **Verification**: `scripts/test_flow1.py` against Sarah Chen CRM record. PATCH status from 4 → 3, wait 90 s, observed status flipped back to 4 within **~8 seconds** (`CHANGELOG.md:76`).
- **Build-time scope reduction**: a third action — update canonical's `aurum_last_refined_date` — was dropped during build because it requires resolving the staging row's `aurum_canonical_customer` lookup to a canonical Row ID, which is a separate Get-a-Row + lookup-binding step. Demo-visible narrative is the staging flip; canonical timestamp sync is now a Phase 5 polish item documented in `ROADMAP.md`.

#### Flow 2 — `AURUM | REFINE | Steward Review Required (CRM)`

- **Trigger**: same shape as Flow 1, on the same table.
- **Filter** (OData): `aurum_match_confidence ge 0.55 and aurum_match_confidence lt 0.65 and aurum_processing_status eq 3`.
- **Action**: Update staging row, set `aurum_processing_status = 5` (`STEWARD_REVIEW`). Teams notification deliberately skipped (locked decision; one-record connector setup not justified for the borderline volume).
- **Verification**: `scripts/test_flow2.py` against Mohammed Al-Rashid CRM record. PATCH status to 3, wait 90 s, observed status flipped back to 5 in **~24 seconds** (`CHANGELOG.md:18`). Workflow registry confirms `category=Modern Flow, statecode=Activated`.

> [SCREENSHOT: Cloud flows list — Flow 1 and Flow 2 both ON]
> [SCREENSHOT: Mohammed CRM record post-Flow-2 routing]

#### Flow 3 — `AURUM | UNEARTH+MARK | Promote Unmatched to Canonical (CRM)` — **deferred**

Different architectural shape from Flows 1 and 2: manual instant trigger ("When a row is selected"), create-row action against the canonical, multi-field mapping (~16 fields with per-source variations), and a lookup re-link on the staging row. Spec is fully locked in `docs/phase4_flow_specifications.md` with the trust-score formula verified against `~/Projects/AURUM/refine/golden_record/survivorship.py:194-205` (canonical trust score for single-source promotion of a 6/6-field-populated prospect = `0.73`, `is_golden = True`). Build estimated at 45–60 min. Deferred for architectural correctness (warranting fresh focus over a tail-end-of-session attempt), not skipped.

---

## 4. Touchpoints with the AURUM GitHub repo

This section is the load-bearing defense of the "vendor-neutral architecture" claim. Four concrete dependencies cross from AURUM-PP into the public AURUM tree:

### 4.1 The matcher import

`scripts/load_sample_data.py` injects `~/Projects/AURUM` onto `sys.path` and imports `score_pair` from `refine.matching.matcher`. Every composite confidence score on every staging record was produced by calling that function. The script also runs `git rev-parse HEAD` against the AURUM working tree and writes the resulting commit into the auto-generated lineage document, so the matcher version in effect is auditable per run.

### 4.2 The trust-score formula citation

Flow 3's trust-score arithmetic is verified against `refine/golden_record/survivorship.py:194-205`:

```python
key_fields = ["first_name", "last_name", "email", "phone", "city", "country"]   # 6 fields
filled = sum(1 for f in key_fields if golden.get(f, "").strip())
completeness = filled / len(key_fields)
diversity    = min(len(distinct_sources) / 3, 1.0)
trust_score  = round(0.6 * completeness + 0.4 * diversity, 2)
is_golden    = trust_score >= 0.6
```

For a single-source promotion with all six fields populated: `completeness = 1.0`, `diversity = 1/3`, `trust_score = 0.6 × 1.0 + 0.4 × 0.333 = 0.7333 → rounds to 0.73`, `is_golden = True`. Phase 4's Flow 3 specification carries `trust_score = 0.73` not as a placeholder but as the value produced by the canonical AURUM survivorship formula.

### 4.3 The five-stage architecture pattern

ASSAY → UNEARTH → REFINE → UNFURL → MARK is adopted verbatim from AURUM, including each stage's purpose statement. AURUM-PP names artifacts (`aurum_assay_profile`, REFINE flows) using these stage labels so that anyone reading the AURUM repo's documentation finds the same vocabulary in AURUM-PP's table list.

### 4.4 Enum source-of-truth

`ProcessingStatus`, `MatchMethod`, `AssaySeverity`, `CRMSegment`, `LoyaltyTier`, and `StewardReviewStatus` are all defined in `scripts/load_sample_data.py:157-192`. When Phase 4's flow specifications reference values like "STEWARD_REVIEW = 5" or "MATCHED = 3", they cite these enum classes. This discipline caught a Phase 3 spec-doc bug (`STEWARD_REVIEW` and `SURVIVED` had been swapped in an early spec draft) and a Phase 4 trigger reformulation (the verbal spec said `aurum_processing_status = UNMATCHED (6)`, but value 6 is `REJECTED`; UNMATCHED lives in `MatchMethod`, not `ProcessingStatus`). The pattern is recorded in memory as `feedback_spec_enum_source_of_truth.md`.

AURUM-PP and the AURUM matcher live in the same repository (since 2026-05-04) but on opposite sides of the implementation boundary: the matcher is Python under `refine/`; AURUM-PP is Power Platform configuration plus deployment scripts under `power-platform/`. The matcher is imported across that boundary unmodified, with no AURUM-PP-specific code on the matcher side. Co-located, not coupled — the architecture's separation of concerns survives the repo layout.

---

## 5. Infrastructure as Code posture (honest framing)

The cleanest version of this story is laid out in `DEFENSE_BRIEF.md`'s 2026-05-04 entry. Repeated here for completeness.

### What is IaC

- **Dataverse schemas** — 100% scripted via `scripts/deploy_table.py` reading `dataverse-schemas/*.yaml`.
- **Sample data** — 100% scripted via `scripts/load_sample_data.py`, including the lineage document that auto-regenerates per run.
- **Authentication** — env-var-driven (`AURUM_PP_DATAVERSE_URL`), MSAL public-client device-code flow, no hardcoded credentials. Token cached at `~/.aurum-pp/token.json` outside the repo.
- **Verification** — `scripts/verify_env_columns.py` for schema drift; `scripts/test_flow1.py`, `scripts/test_flow2.py` for flow behavior. Each flow gets a regression test before activation.

### What is not yet IaC

- **Model-driven app** built in maker UI.
- **Custom views** built in maker UI (sitemap XML is hand-authored — partial step toward IaC).
- **Cloud flows** built in maker UI.

### The migration path

A solution-export-based pipeline is documented in `ROADMAP.md` as Phase 5+ work: export the AURUM Master Data Management solution as a managed `.zip` via the Web API, mutate `Workflows/{guid}.json` inside the archive per a flow YAML spec, re-import via PAC CLI or solution import API. This is the Microsoft-documented ALM path. A spike on Day 3 morning confirmed that `POST /workflows` against `category=5` (modern cloud flows) is undocumented and community-reported as fragile (orphan records, broken connection-reference binding). The investigation is summarized in `CHANGELOG.md` 2026-05-04 entry.

Estimated effort for the first solution-export build: 60–90 minutes. Estimated incremental cost per additional flow once the pipeline exists: ~5 minutes. Trigger to revisit: when ECOMM/LOYALTY flow replication (six more flows) justifies the upfront cost.

### Why the honest framing matters

Overclaiming "fully IaC" damages credibility the moment a colleague who knows the maker UI was used asks how the flows were authored. "Hybrid IaC with a documented migration path" is accurate, defensible, and matches the maturity ladder enterprise Power Platform shops climb. It also frames the open work as deliberate progression rather than a hidden gap.

---

## 6. Reality Auditor moments

These are surfaced specifically because they teach. Each one is a place where the path of least resistance was wrong, and where verifying against source-of-truth was the only way to keep the project honest.

- **The matcher hallucination (Day 2 morning).** Composite scores on demo records were initially produced by an invented arithmetic with components like "phone-cluster bonus" that do not exist in `refine/matching/matcher.py`. Caught by reading the actual matcher source. Fix: every demo composite is now `_aurum_score_pair(...)` output, not invented arithmetic. The lineage document regenerates on every load.
- **The trust-score invention (Day 2 evening).** An early Phase 4 draft cited canonical trust score `0.63` (`completeness 0.83 × 0.6 + diversity 0.33 × 0.4`) and asserted `is_golden = False` for single-source promotions. Verified against `survivorship.py:194-205`: actual value for a 6/6-populated prospect is `0.73`, and `is_golden` is `True` (the threshold is 0.6, not 0.7). Phase 4 spec corrected.
- **The Quirk-10 enum conflation (Day 2 evening).** Verbal spec: "Flow 3 trigger filter is `aurum_processing_status = UNMATCHED (6)`." `ProcessingStatus.6 = REJECTED`. `UNMATCHED` lives in `MatchMethod`, not `ProcessingStatus`. Flow 3 trigger reformulated to `aurum_match_method = 5 AND aurum_canonical_customer IS NULL`. The lesson — never infer enum values from semantic context, always read the source — is now the project rule (`feedback_spec_enum_source_of_truth.md`).
- **The undocumented `POST /workflows` path (Day 3 morning).** When the agent considered building Flow 2 programmatically, the investigation step confirmed that GET and PATCH on the workflows entity are documented for `category=5`, but POST creation is not. Stopped per project rule "if blocked or undocumented, fall back to maker UI." Solution-export pipeline added to ROADMAP as the documented programmatic path. The discipline here is: the temptation was to try and see what happens; the correct move was to read the documented surface, conclude it was incomplete, and report back rather than experiment with creation calls that could have polluted the tenant.
- **The DEFENSE_BRIEF scope creep (Day 3 morning).** When asked to add a verbatim section to DEFENSE_BRIEF, the agent appended an extra explanatory paragraph beyond the user's spec. Self-corrected and reverted. Small but worth surfacing: scope discipline applies even to documentation edits.

---

## 7. Open risks and gaps

Listed without softening. Most have explicit "trigger to revisit" entries in `ROADMAP.md`.

- **Forms auto-generated.** Default Dataverse forms do not foreground `aurum_match_confidence` or lineage fields. Phase 5 custom-form work pending.
- **Sitemap reorganization deferred.** Per-table groups today; AURUM stage groups (ASSAY, UNEARTH, REFINE, UNFURL) blocked by maker UI sitemap-designer bug.
- **Flow 3 not yet built.** Spec locked, build estimated at 45–60 min; deferred for fresh focus.
- **ECOMM and LOYALTY flow replication not done.** Six additional flows. Estimated 60 min total. Triggers the solution-export pipeline build.
- **Anti-match rule for conflicting discriminators deferred to AURUM v0.3.0** (cross-repo). Audit confirmed zero current demo records would shift under the rule (`docs/phase4_anti_match_audit.md`); building flow infrastructure for an un-exercised rule violates "ship working tools." The architectural fit is also wrong — anti-match is matching logic, belongs in `refine/matching/matcher.py`, not in Power Automate workflow.
- **Power Automate trigger latency dependency.** 8 s and 24 s end-to-end observed; Microsoft does not contractually SLA Dataverse-trigger latency. These are demo-grade, not production-grade, observations.
- **DLP policies could block flows** in tenants with strict business/non-business connector splits. Currently observed in a default Developer Plan environment with no DLP policy applied.
- **Choice field integer-vs-label coupling (Quirk 10 surface).** YAML, deploy script, and env each carry choice integer values; drift between any two is silent, only caught by `verify_env_columns.py` after the fact. A YAML-side equivalent (`verify_yamls_match_env.py`) is in the deferred backlog.
- **Canonical `last_refined_date` sync deferred** (Phase 5 polish). Flow 1 currently doesn't update the canonical's timestamp because the lookup-resolution step was dropped during build.
- **No PII handling for production data.** Sample data is synthetic; nothing in this project has been exercised against real customer data, real PII normalization, or jurisdiction-specific privacy constraints.
- **No multi-tenant isolation tested.** AURUM-PP has been deployed and exercised in a single Developer Plan environment.
- **Connection reference dependency.** Every flow imports `aurum_sharedcommondataserviceforapps_8e3b2`. Environment promotion (dev → test → prod) requires connection re-binding in each target environment.
- **`aurum_household_head` family deployed but unused.** Three columns sit on canonical and LOYALTY without being populated by the demo data load. Either wire into a future household-grouping demo or remove from env. Surfaced via `docs/env_column_manifest_2026-05-03.md`.

---

## 8. Reliability and trust plan

How AURUM-PP graduates from "demo runs cleanly" to "could survive a real ingestion stream."

- **Dataverse audit log captures every flow modification** by default (per-table `is_audit_enabled: true` set in every YAML). Steward can view audit history per record.
- **Source-of-truth verified enums.** `load_sample_data.py:157-192` is canonical for all picklist values. The `feedback_spec_enum_source_of_truth.md` memory entry codifies the rule: never infer picklist values from semantic context; read the actual enum class.
- **Web API testing harness.** `test_flow1.py`, `test_flow2.py`, and the future `test_flow3.py` give regression coverage that's independent of Power Automate UI runs. Every flow gets a verifier before activation.
- **Phased flow buildout.** One flow at a time, end-to-end-validated before the next starts. Flow 3 work does not begin until Flow 2 is green.
- **Public AURUM repo as the matcher dependency source.** The matcher is upgrade-tracked rather than vendored; an AURUM v0.3.0 release with anti-match rules will be picked up by AURUM-PP via a commit-pin update, not a parallel re-implementation.
- **Solution-export pipeline (Phase 5)** closes the IaC gap on the maker-UI components.
- **Anti-match rules in AURUM v0.3.0** close the conflicting-discriminator gap.
- **Documentation discipline.** Every project carries `PROJECT_HISTORY.md` (narrative), `CHANGELOG.md` (per-change), `ROADMAP.md` (forward-looking), `DEFENSE_BRIEF.md` (defense talking points). AURUM-PP also carries the auto-regenerated `docs/demo_records_aurum_lineage.md`, which makes the matcher's per-pair output a first-class artifact.

---

## 9. Demo narrative arcs

Three scenarios stewards observe. The arc is short on purpose: the platform speaks for itself when the data is honest.

### Scenario 1 — Auto-approval (Sarah Chen)

Sarah's CRM record carries `aurum_match_confidence = 1.00`, `aurum_match_method = 1` (`EXACT`), `aurum_processing_status = 3` (`MATCHED`). Any modification on the record fires Flow 1; within ~8 seconds, status flips to 4 (`SURVIVED`). The steward sees nothing — the high-confidence path is automated. The same pattern would handle Aisha Mubarak (CRM and LOYALTY both `1.00`) and Priya Krishnamurthy (ECOMM `0.89`, LOYALTY `1.00`).

> [SCREENSHOT: Sarah Chen CRM record post-Flow-1 auto-approve]

### Scenario 2 — Steward review (Mohammed Al-Rashid)

Mohammed's CRM record carries `aurum_match_confidence = 0.60`, `aurum_match_method = 3` (`FUZZY_BORDERLINE`). He sits in the band where the matcher has surfaced him as a candidate but has not crossed the auto-approve threshold. Flow 2 routes him to `aurum_processing_status = 5` (`STEWARD_REVIEW`) within ~24 seconds. Mohammed appears in the CRM `Pending Steward Review` view. The steward exercises judgment — merge with the existing canonical Mohammed Al-Rashid, or keep separate as a distinct entity.

> [SCREENSHOT: Pending Steward Review queue with Mohammed]

### Scenario 3 — Promote unmatched (Hassan Bin Saeed) — pending Flow 3

Hassan has `aurum_match_method = 5` (`UNMATCHED`) and `aurum_canonical_customer IS NULL`. The steward, after reviewing the staging record, selects Hassan in the model-driven app and clicks the "Promote to Canonical" instant-trigger flow. Flow 3 creates a new `aurum_customer` row populated from CRM staging fields, computes `trust_score = 0.73` and `is_golden = True` per the survivorship formula, links the staging row's `aurum_canonical_customer` lookup to the new canonical, and sets staging `aurum_processing_status = 4`. Same shape applies to Joana Reyes (CRM), Lukas Weber (ECOMM, with shipping-address mapping), and Maria L Santos (LOYALTY, with `_parsed` name mapping).

This scenario does not fire today. The flow is spec-locked and pending build.

---

## 10. What's next

**Day 4.**

- Build Flow 3 — Promote Unmatched to Canonical (CRM only). Estimated 45–60 min.
- Capture screenshots of all three flows for the touchpoint document and the eventual public write-up.
- Optional: ECOMM and LOYALTY flow replication, executed via the Phase 5 solution-export pipeline rather than per-flow maker-UI clicks.

**Phase 5+.**

- Form customization per `docs/phase3_forms_specification.md`.
- Sitemap reorganization into AURUM stage groups (ASSAY / UNEARTH / REFINE / UNFURL navigation).
- Solution-export-based flow IaC pipeline.
- Anti-match rule landed in AURUM v0.3.0; AURUM-PP regenerates sample data with the "Sarah Chen Dubai" anti-match exemplar.
- `last_refined_date` sync added to all three Flow 1 instances.

---

## 11. References

- Public AURUM repo: `https://github.com/RajaMDM/AURUM`
- AURUM-PP within AURUM: `https://github.com/RajaMDM/AURUM/tree/main/power-platform`
- Internal documents (in repo): `CHANGELOG.md`, `ROADMAP.md`, `DEFENSE_BRIEF.md`, `README.md`, `docs/phase4_flow_specifications.md`, `docs/phase4_anti_match_audit.md`, `docs/demo_records_aurum_lineage.md`, `docs/phase3_views_specification.md`, `docs/phase3_sitemap_walkthrough.md`, `docs/phase3_forms_specification.md`.
- Memory-resident knowledge (Claude Code memory, not in repo): `project_aurum_pp_dataverse_quirks.md` (11 quirks), `feedback_spec_enum_source_of_truth.md`, `feedback_aurum_pp_tenant_redaction.md`, `feedback_verify_dataverse_state_via_webapi.md`, `project_aurum_pp_table_conventions.md`.
- LinkedIn: `linkedin.com/in/raja-shahnawaz/`.
- Built by Raja Shahnawaz Soni (architect), Claude Code (build agent), Cowork (this document).
