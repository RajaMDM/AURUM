# AURUM-PP Changelog

Every significant change with date, what changed, why, and business impact. Companion to `PROJECT_HISTORY.md` (narrative), `TECH_MEMORY.md` (decisions), `ROADMAP.md` (forward-looking), `DEFENSE_BRIEF.md` (defense talking points). Newest first.

## 2026-05-04 — Day 3 morning

Phase 4 progressed from 1-of-3 to 2-of-3 flows live. End of session.

### Phase 4 — Power Automate flows 🟡 PARTIAL (2 of 3 built)

**Flow 1 — Auto-Approve High-Confidence Match (CRM)** ✅ verified working (carried over from Day 2)
- End-to-end latency ~**8s** on Sarah Chen test (yesterday).

**Flow 2 — Steward Review Required (CRM)** ✅ COMPLETE
- Built in maker UI (after Reality Auditor stop on programmatic POST attempt — see below). Activated.
- Trigger: `aurum_match_confidence >= 0.55 AND < 0.65 AND aurum_processing_status = 3 (MATCHED)` on `aurum_crm_customer`.
- Action: Update staging row's `aurum_processing_status = 5 (STEWARD_REVIEW)`. Teams notification skipped per locked decision.
- **Verified end-to-end via `scripts/test_flow2.py` on Mohammed Al-Rashid CRM record:** PATCH staging status to 3, wait, status flipped back to 5 in **~24 seconds**. Workflow registry confirms `category=Modern Flow, statecode=Activated`.

**Flow 3 — Promote Unmatched to Canonical (CRM)** ⏸ DEFERRED to next session
- Architecturally different shape (manual instant trigger + create-row + multi-field map + canonical lookup relink) warrants fresh focus rather than tail-end-of-session build. Spec already locked in `docs/phase4_flow_specifications.md`.

### Reality Auditor catches this session

- **Programmatic flow deployment investigated and stopped at feasibility gate.** Considered building Flow 2 via `POST /workflows`. Step 1 investigation confirmed: GET/PATCH on workflows entity is documented for `category=5` (modern cloud flows), but POST creation is undocumented and community-reported as fragile (orphan records, broken connection-reference binding). Stopped per project rule "if blocked or undocumented, fall back". Maker UI used for Flow 2; solution-export-based IaC pipeline added to ROADMAP Phase 5+ as the documented programmatic path.
- **DEFENSE_BRIEF edit scope-creep self-corrected.** Added an extra explanatory paragraph beyond the user-specified verbatim text; caught and reverted to spec.

### Documentation delivered Day 3 morning

- `ROADMAP.md` — added "Phase 5+ — Solution-export-based flow IaC pipeline" section with trigger, 4-step approach, effort estimate, and Day 3 blocker context.
- `DEFENSE_BRIEF.md` — added 2026-05-04 "On 'AURUM-PP is IaC' claims" section (hybrid-IaC framing).
- Memory drift fix — `project_aurum_pp.md` and `project_aurum_pp_resume_next_session.md` updated to reflect new working dir (`~/Projects/AURUM/power-platform/`, not `~/Projects/AURUM-PP/`) and Day 3 phase state.

## 2026-05-03 — Day 2 wrap (end of day)

End of a long, productive day. Phase 1 → Phase 4 partial. Major project momentum.

### Phase 1 — Dataverse schema deploy ✅ COMPLETE

Deployed all 5 Dataverse tables to AURUM-PP-Dev environment via Python+MSAL+Web API path (after PAC CLI 2.6.4 incompatibility with macOS .NET 10 forced architecture pivot). Tables: `aurum_customer` (canonical), `aurum_crm_customer`, `aurum_ecomm_customer`, `aurum_loyalty_customer` (3 staging), `aurum_assay_profile` (assay).

**Why this approach:** PAC CLI broker NRE on macOS made the Microsoft-recommended PAC path unviable. Python+MSAL+Web API is more code but gives full control over schema metadata, repeatable deploys via YAML, and avoids the .NET runtime dependency. Trade-off accepted for cross-platform compatibility.

**Business impact:** Dataverse schema is now reproducible from `dataverse/schemas/*.yaml` in <2 minutes via `python scripts/deploy_table.py`. New environments (test, prod) deployable from same source.

**Quirks captured: 11** in `project_aurum_pp_dataverse_quirks.md` memory — IsValidForAdvancedFind shape asymmetries, IsPrimaryName triumvirate, calc-field XAML deferral, auto-companion columns, silently-ignored lookup audit, Email-primary support, MaxLength-on-calc-fields behavior, PK auto-naming convention, **YAML+script vs env drift (Quirk 10 + corollary, N=4 occurrences)** — plus code-review defense talking points and the meta-pattern: always verify env via Web API before treating YAMLs or scripts as authoritative.

### Phase 2 — Sample data load ✅ COMPLETE

Built `scripts/load_sample_data.py` (~2200 LOC). Inserted **96 demo records** across all 5 tables: 30 canonicals, 23 CRM staging, 20 ECOMM staging, 15 LOYALTY staging, 8 assay findings. Manifest at `scripts/sample_data_manifest_20260503.json`.

**Real AURUM matcher integration:** hard-imports `score_pair()` from public AURUM repo at `~/Projects/AURUM` (commit `78223b64c2bb`). All confidence values for the 5 demo-story records (Priya, Mohammed, Sarah, Aisha, prospect cluster) come from the actual matcher, not hand-tuned. Re-derived after a mid-build catch where invented arithmetic was used (`+0.25 phone-cluster` etc.) — caught and corrected to honor "the architecture is the source of truth, not spec values I invented."

**Business impact:** demo records are reproducible, mathematically honest, and tied to a specific matcher commit. Lineage doc `docs/demo_records_aurum_lineage.md` auto-regenerates on every script invocation, capturing per-pair matcher breakdowns. Single source of truth from script → markdown → demo narrative.

**Tooling delivered:** `scripts/verify_env_columns.py` performs systematic env-vs-script drift verification across all 5 tables (Quirk 10 prevention). Manifest at `docs/env_column_manifest_2026-05-03.md`.

### Phase 3 — Model-driven app + steward views ✅ COMPLETE

Built **AURUM Steward Workbench** model-driven app in maker UI. Sitemap structured by AURUM 5-stage architecture (ASSAY → UNEARTH → REFINE → UNFURL — MARK absent until Phase 4 lineage table). Plain-text titles (emoji deferred — uncertain rendering across browser/OS).

**System views built (3 instances each):** Pending Steward Review on `aurum_crm_customer`, `aurum_ecomm_customer`, `aurum_loyalty_customer` (LOYALTY uses `_parsed` suffix for name fields per design — verified pre-build).

**Forms:** auto-generated, deferred to Phase 5 polish.

**Pre-build doc-correctness work:** caught and patched 3 spec blockers via `feedback_spec_enum_source_of_truth.md` discipline — ProcessingStatus values were swapped (STEWARD_REVIEW=5 vs SURVIVED=4 in spec), AssaySeverity filter values were wrong (would have hidden Critical findings), severity sort direction was inverted. Source-of-truth verification now mandatory for any spec doc referencing enum values.

**Business impact:** steward has working UI to triage matches by source. App published with status=On.

### Phase 4 — Power Automate flows 🟡 PARTIAL (1 of 3 built)

**Flow 1 — Auto-Approve High-Confidence Match (CRM)** ✅ COMPLETE
- Trigger: row added/modified on `aurum_crm_customer` where `aurum_match_confidence >= 0.85 AND aurum_processing_status = 3 (MATCHED)`
- Action: Update staging row's `aurum_processing_status = 4 (SURVIVED)`
- 3-node flow (Trigger + Condition + Update). Activated.
- **Verified end-to-end via `scripts/test_flow1.py` on Sarah Chen CRM record:** PATCH staging status from 4→3, wait 90s, status flipped back to 4 in **~8 seconds**. Fast.
- Build-time scope reduction: original spec had a 3rd action (update canonical's `aurum_last_refined_date`). **Dropped** — `aurum_last_refined_date` is on canonical only, requires lookup-resolution to update from staging trigger. Demo's visible narrative is the staging flip; canonical timestamp sync deferred to Phase 5 polish (entry in ROADMAP.md).

**Flow 2 — Steward Review Required (CRM)** ⏸ NOT BUILT
- Trigger spec: `aurum_match_confidence >= 0.55 AND < 0.65 AND aurum_processing_status = 3 (MATCHED)`
- Action: Update staging row's `aurum_processing_status = 5 (STEWARD_REVIEW)`
- Teams notification SKIPPED for tonight (locked decision).
- Test subject: Mohammed Al-Rashid CRM (composite=0.60, only borderline-band demo record).

**Flow 3 — Promote Unmatched to Canonical (CRM)** ⏸ NOT BUILT
- Trigger spec: manual instant trigger ("When a row is selected"). Locked Option A.
- Action: create new `aurum_customer` from staging fields, set trust_score=0.73 (verified formula from `~/Projects/AURUM/refine/golden_record/survivorship.py:194-205`), update staging.
- Test subjects: Hassan Bin Saeed or Joana Reyes (CRM prospects).

**Scope decision:** CRM-only for tonight. ECOMM/LOYALTY replication deferred to Phase 5.

### Mohammed CRM record state — note for Day 3 morning

Pre-flight test of Flow 2 PATCHed Mohammed's `aurum_processing_status` from `5` (STEWARD_REVIEW) to `3` (MATCHED) to satisfy Flow 2's trigger filter. Flow 2 isn't built yet, so **Mohammed remains at status=3** in env until either:

- **(a, recommended)** Day 3's first action builds Flow 2 → flow auto-fires on Mohammed's existing modified state → flips him back to 5. Uses Flow 2's first run as its own test.
- **(b)** Manually PATCH Mohammed back to 5 first if a clean baseline is preferred before building.

Mohammed CRM GUID: `38f041fa-c046-f111-bec7-6045bdcde568`. Source ID: `CRM-00219`.

### Tooling delivered Day 2

- `scripts/auth.py` — MSAL device-code authentication
- `scripts/deploy_table.py` — YAML→Web API deployer (909 LOC)
- `scripts/load_sample_data.py` — sample data generator with real AURUM matcher (~2200 LOC)
- `scripts/verify_env_columns.py` — Quirk 10 verification across all 5 tables
- `scripts/generate_sitemap.py` — Phase 3 doc generator (sitemap XML + walkthrough + views spec + forms spec)
- `scripts/test_flow1.py` — Flow 1 end-to-end verifier
- `scripts/test_flow2.py` — Flow 2 end-to-end verifier (ready for Day 3 use)

### Documentation delivered Day 2

- `README.md`, `ROADMAP.md`, `CHANGELOG.md` (this file)
- `docs/demo_records_aurum_lineage.md` (auto-generated, 280+ lines, per-pair matcher breakdowns)
- `docs/env_column_manifest_2026-05-03.md` (auto-generated, 5-table drift surface)
- `docs/phase3_sitemap_walkthrough.md`, `docs/phase3_views_specification.md`, `docs/phase3_forms_specification.md`
- `docs/phase4_flow_specifications.md`, `docs/phase4_anti_match_audit.md`

### Memory captured Day 2

- `project_aurum_pp_dataverse_quirks.md` — 10 quirks + Quirk 10 corollary
- `feedback_verify_dataverse_state_via_webapi.md`
- `feedback_spec_enum_source_of_truth.md` — caught 2 instances of spec-vs-source-of-truth drift
- `feedback_aurum_pp_tenant_redaction.md`, `feedback_stale_customer_yaml.md`
- `project_aurum_pp_design_decisions.md`, `project_aurum_pp_table_conventions.md`, `project_aurum_pp_changelog.md`, `project_aurum_pp.md`
- MEMORY.md index updated with Phase 2 ✅ complete + 11-quirks marker
