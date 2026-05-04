# AURUM-PP Roadmap

Forward-looking planning doc. Where the project is heading, what's blocked, what triggers the next phase. Companion to `PROJECT_HISTORY.md` (chronological narrative), `TECH_MEMORY.md` (architectural decisions), `CHANGELOG.md` (per-change log), `DEFENSE_BRIEF.md` (defense talking points).

## Phase status (as of 2026-05-04 morning)

| Phase | Status | Description |
|---|---|---|
| Phase 1 — schema deploy | ✅ complete | All 5 Dataverse tables deployed via Python+MSAL+Web API. 11 quirks captured. |
| Phase 2 — sample data load | ✅ complete | 96 demo records inserted with real AURUM matcher integration (commit `78223b64c2bb`). |
| Phase 3 — model-driven app + steward views | ✅ complete | AURUM Steward Workbench published. 3 Pending Steward Review views built (CRM/ECOMM/LOYALTY). Forms auto-generated, deferred to Phase 5. |
| Phase 4 — Power Automate flows | 🟡 partial (2 of 3) | Flow 1 (Auto-Approve, ~8s) and Flow 2 (Steward Review, ~24s) both verified for CRM. Flow 3 deferred to Day 4. |
| Phase 5+ | not started | Polish, ECOMM/LOYALTY replication, dashboards, solution-export IaC pipeline. See "Future phases" + deferred backlog below. |

## Day 4 plan

1. **Build Flow 3 — Promote Unmatched to Canonical (CRM)** — manual instant trigger (Option A locked). Test subjects: Hassan Bin Saeed or Joana Reyes (CRM prospects). Field mapping is verbose; trust_score=0.73 formula already verified. **~45–60 min** build.
2. **Capture screenshots of all 3 flows** for blog/touchpoint use.
3. **Expand `docs/TOMORROW_TECHNICAL_TOUCHPOINT.md`** from skeleton to full doc — work and students audiences both addressed.
4. **Optional:** ECOMM/LOYALTY flow replication via solution-export IaC pipeline (Phase 5 work — see below).

## Deferred backlog (Phase 5 cleanup tomorrow)

These are explicit deferrals from Day 2 Phase 1–4 work. Pick up in Phase 5:

1. **Flow 1 enhancement: canonical `last_refined_date` sync** — see "Flow 1 enhancement" section below. ~5 min × 3 instances.
2. **ECOMM/LOYALTY flow replication** — Flow 1 + Flow 2 + Flow 3 replicated to ECOMM and LOYALTY staging tables. ~6 additional flows. ~60 min total.
3. **Form customization** — replace auto-generated forms with the per-tab layouts spec'd in `docs/phase3_forms_specification.md`. ~30 min.
4. **Sitemap reorganization** — current sitemap is per-table groups. Phase 5 polish reorganizes into AURUM 5-stage groups (ASSAY, UNEARTH, REFINE, UNFURL) per `docs/phase3_sitemap_walkthrough.md`'s original design. ~10 min in app designer.
5. **Anti-match rule for AURUM v0.3.0 (cross-repo)** — see "AURUM v0.3.0 — Anti-match rules" section below. Adds ~10 LOC to public AURUM matcher + new demo record. Bumps AURUM commit pin.

## Open backlog items deferred to later phases

## Open backlog items deferred to later phases

### `aurum_household_head` family — deployed but not used

Three columns are deployed in env but never populated by the demo data load:
- `aurum_customer.aurum_household_head` (Lookup, self-referential)
- `aurum_customer.aurum_household_headname` (String, Quirk 4 auto-companion)
- `aurum_loyalty_customer.aurum_household_head_member_number` (String)

**Resolution path (decision deferred to post-Phase-7 cleanup):**
- (a) Wire into a Phase 4+ household-grouping flow demo (one canonical owns N other canonicals as household members; useful for the AURUM REFINE → UNFURL story when the household concept becomes load-bearing for survivorship)
- (b) Remove from env if no near-term demo use materializes (reduces "missing-from-script" noise in `verify_env_columns.py` output)

**Trigger to revisit:** when the demo narrative needs to include a household-grouping step, OR when surface-area cleanup becomes worth a focused 30-min PR.

**Surfaced via:** `docs/env_column_manifest_2026-05-03.md` "missing-from-script" diff — these were the only 3 missing aurum_ columns that don't fall into the auto-companion / calc-field / Quirk-categories of expected gaps.

### Calc field synthesis (per Quirk 3)

`aurum_crm_customer.aurum_full_name_display` was deferred to manual maker UI creation because Dataverse's Web API requires calc-column FormulaDefinition as compiled XAML, not the simple-text expression you see in maker. Synthesizing valid calc-XAML programmatically is significant R&D for one column.

**Trigger to invest in XAML synthesis:** when 3+ AURUM-PP tables require calc fields, the per-table cost of manual creation justifies the tooling investment.

### Flow 1 enhancement — canonical `last_refined_date` sync (Phase 5 polish)

**Deferred from Phase 4 build (2026-05-03):** Flow 1 originally spec'd a 3-step action sequence (condition → update staging → update canonical). Action 3 (update canonical's `aurum_last_refined_date`) was dropped during build — `aurum_last_refined_date` lives on canonical only, so updating it requires resolving the `aurum_canonical_customer` lookup on the trigger row to a canonical Row ID (one extra Get-a-Row action + lookup-binding wiring).

**Why deferred, not a bug:** the demo's visible narrative is the staging status flip (MATCHED → SURVIVED) which Flow 1 handles correctly in 8s end-to-end. Audit of the staging row is captured by Dataverse built-in `modifiedon`. Building action 3 would have blocked Flow 2 + Flow 3 work in the time-boxed Phase 4 session.

**Phase 5 scope:** add an "Update a row" action to Flow 1 (CRM, ECOMM, LOYALTY) that:
1. Reads `aurum_canonical_customer` lookup off the trigger row (Power Automate dynamic content — pick the *Value* / GUID, not the *Name*)
2. Updates `aurum_customer` row at that GUID with `aurum_last_refined_date = utcNow()`
3. Time estimate: ~5 min per Flow 1 instance × 3 staging tables = 15 min total

**Trigger to do this:** Phase 5 cleanup work, OR when a future demo specifically needs to show canonical timestamps advancing in real-time.

### AURUM v0.3.0 — Anti-match rules (cross-repo, Phase 5)

**Design intent (locked Phase 4 prep, 2026-05-03):** When two records have a strong name match but conflicting discriminators (e.g., different phone numbers), the matcher should signal `discriminator_conflict` so downstream consumers route to STEWARD_REVIEW regardless of composite score. Discriminator conflict on a contact channel is suspicious enough to warrant human judgment even when the composite score says "confident match."

**Why deferred from Phase 4:** Audit (`docs/phase4_anti_match_audit.md`) found 0 of 6 high-confidence demo records would shift under this rule (all phones aligned by structural design — phone is a positive matcher signal, so high-conf pairs almost always have aligned phones). Building flow-level infrastructure with no test scenario violates "ship working tools." Architectural fit is also wrong — anti-match logic is matching logic, belongs in `~/Projects/AURUM/refine/matching/matcher.py`, not Power Automate workflow.

**Phase 5 scope:**
- **AURUM repo (`~/Projects/AURUM/`)**: add anti-match check after composite calc in `score_pair()`. Add `discriminator_conflict: bool` field to `MatchCandidate` dataclass. ~10 LOC + tests. Bump to v0.3.0.
- **AURUM-PP**: regenerate sample data with one demo record exercising the rule. Suggested: "Sarah Chen Dubai" — same name + email as canonical Sarah, different phone (digits swapped). Should land at composite ≥0.85 via name_boost_floor (name=1.0, email=1.0, phone=0 → weighted=0.90, floor=0.85), then `discriminator_conflict=True` flips processing_status to STEWARD_REVIEW. Bump `AURUM_PP_AURUM_COMMIT_PIN` to v0.3.0 commit hash.
- **Flow layer**: no Flow 1 changes (its filter already excludes records the matcher set to STEWARD_REVIEW). Existing Flow 2 picks up the new state via its existing filter.

**Trigger to do this:** when starting Phase 5 cleanup work tomorrow, OR when a future demo record genuinely needs anti-match coverage (whichever comes first).

### `verify_yamls_match_env.py` (per Quirk 10)

Quirk 10 captured 3 YAML-vs-env drift cases during table deploy. The 2026-05-03 ghost column added a 4th case (script-vs-env). `verify_env_columns.py` exists for the script side; an analogous YAML-side verification script should exist before any future schema-extension work.

**Trigger:** before authoring Phase 3+ schema additions, OR when adding a 6th table.

## Phase 5+ — Solution-export-based flow IaC pipeline

Trigger to revisit: when ECOMM/LOYALTY flow replication (6 more flows) justifies the upfront cost.

Approach:
  1. Export AURUM Master Data Management solution as managed .zip via Web API
  2. Programmatic mutation of Workflows/{guid}.json inside the .zip per flow YAML spec
  3. Re-import via PAC CLI or solution import API
  4. Microsoft-documented ALM pattern (defensible IaC story, unlike POST hacks to /workflows)

Estimated effort: 60-90 min for first build (Phase 5 work). Then ~5 min per additional flow.

Verified blocker (Day 3 morning): POST /workflows for category=5 (modern cloud flows) is undocumented and community-reported as fragile. Solution-export pattern is the documented path.

## Future phases (sketch — not committed)

- **Phase 3 — survivorship rule engine**: implement REFINE-stage canonical merging. Trust score computation already partially in place via `aurum_trust_score` / `aurum_completeness_score` / `aurum_diversity_score`; needs the merge logic that resolves conflicts across 3 staging sources into 1 canonical.
- **Phase 4 — Power Apps canvas app**: steward-review UI. Show borderline-band match candidates (Mohammed pattern), accept/reject decisions, write back to canonical. The "human-in-the-loop" half of REFINE.
- **Phase 5 — Power Automate flow**: orchestrate the 5-stage pipeline. Trigger on new staging records, run REFINE matching, surface borderline cases via Phase 4 UI, write canonical updates.
- **Phase 6 — assay dashboard**: Power BI or model-driven app reading from `aurum_assay_profile`. The ASSAY-stage visibility surface.
- **Phase 7 — production-style hardening**: error retry, dead-letter queue, observability. Move from "demo runs cleanly" to "could survive a real ingestion stream."

These are sketches, not commitments. Phase 3 entry condition: Phase 2 lineage doc + manifest validated, real-insert successful end-to-end, demo-narrative tested standalone.
