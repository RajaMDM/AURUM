# Phase 4 — Power Automate flow specifications

Spec for three Power Automate flows that demonstrate AURUM stages REFINE + UNFURL + MARK in motion. Built manually in Power Automate maker UI (`make.powerautomate.com` → AURUM-PP-Dev environment). No automated flow JSON generation — see Architect's brief for rationale.

**Generated 2026-05-03 as Phase 4 prep doc. Source-of-truth values verified against `load_sample_data.py` enum classes + `~/Projects/AURUM/refine/golden_record/survivorship.py` formula.**

## Locked decisions (2026-05-03 17:00, pre-build)

| Decision | Locked value | Rationale |
|---|---|---|
| **Scope for tonight** | **CRM ONLY** — 3 flows total (1 per Flow #), not 9 | ECOMM/LOYALTY replication = Phase 5 cleanup tomorrow. Test subjects: Sarah Chen (Flow 1), Mohammed Al-Rashid (Flow 2), Hassan Bin Saeed or Joana Reyes (Flow 3). |
| **Anti-match rule** | **Option B — defer to AURUM v0.3.0 (Phase 5)** | Audit found 0 of 6 high-conf demo records would shift; Sarah/Aisha/Priya demos NOT broken. Full audit: `docs/phase4_anti_match_audit.md`. ROADMAP entry added. |
| **Flow 3 trigger** | **Option A — manual instant trigger** ("When a row is selected") | Zero schema changes; clean steward UX; one explicit user action per promotion. |
| **Flow 2 Teams notification** | **SKIP for tonight** | Connector setup cost not justified for one demo record (Mohammed). Flow 2 just updates `aurum_processing_status = STEWARD_REVIEW`. Notification = Phase 5+ if value emerges. |
| **Flow 3 trust score** | **Verified formula from `~/Projects/AURUM/refine/golden_record/survivorship.py:194-205`** | See "Flow 3 trust score formula (verified)" section below. Replaces my prior placeholder 0.83/0.33/0.63 — actual value for Hassan/Joana/Lukas/Maria with all 6 key fields populated is **0.73**. |

---

## Source-of-truth values (verified 2026-05-03)

Cited from `scripts/load_sample_data.py`:

```
class ProcessingStatus (lines 166-172):
    LOADED = 1
    PROFILED = 2
    MATCHED = 3
    SURVIVED = 4
    STEWARD_REVIEW = 5
    REJECTED = 6
    # NOTE: there is NO "UNMATCHED" value in this enum

class MatchMethod (lines 157-163):
    EXACT = 1
    FUZZY_HIGH = 2
    FUZZY_BORDERLINE = 3
    STEWARD_APPROVED = 4
    UNMATCHED = 5
    SINGLE_SOURCE_PROMOTION = 6  # LOYALTY only
```

**Critical correction to Phase 4 verbal spec:** the user's verbal spec for Flow 3 referenced `aurum_processing_status = UNMATCHED (6)` — this is incorrect. `aurum_processing_status` value 6 is `REJECTED`, not UNMATCHED. The "unmatched" concept lives in `aurum_match_method = 5` (UNMATCHED) AND `aurum_canonical_customer IS NULL`. Flow 3 trigger reformulated below using the correct combination.

**Matcher thresholds (per `~/Projects/AURUM/refine/matching/matcher.py`):**
- Candidate filter floor: 0.55 (records below this aren't surfaced as candidates)
- Match threshold: 0.65 (composite ≥ this is `is_match=True`, auto-approve to canonical)
- Borderline band: 0.55–0.65 (candidate but below auto-match — steward review territory)

---

## Pre-flight notes

### Teams connector availability

I cannot verify Teams connector availability programmatically — connector lookup is in the Power Apps/Power Automate API surface, not the Dataverse Web API used by `verify_env_columns.py`. **Pragmatic guidance:**
- Teams connector is generally available in default Power Platform environments
- Requires sign-in with M365 credentials when adding the Teams action
- DLP policies (if any) at the tenant level could block it
- **Confirm at Flow 2 build time** — when the maker UI prompts to add a Teams "Post a message" action, you'll either see it or get a connector-blocked error
- **Fallback if blocked:** Flow 2 spec includes a "log to placeholder" alternative (write to a Dataverse note, or skip the notification entirely; flow still updates the staging record)

### Audit trail / MARK stage

User's verbal spec said "audit row (TBD — no audit table yet, use Dataverse audit log or skip)". Resolution per spec:
- **Phase 4 audit posture:** rely on Dataverse's built-in audit log (table-level audit is ON per project conventions). Each row update is captured automatically with user/timestamp/before/after.
- **Custom MARK lineage table** (e.g., `aurum_mark_lineage_event`) deferred to a later phase. The built-in audit log gets us through Phase 4 demo without adding schema.
- Trade-off documented in Architect's brief below.

---

## Flow 1 — AURUM | REFINE | Auto-Approve High-Confidence Match — ✅ COMPLETE (2026-05-03)

**Status:** Built, turned ON, verified end-to-end via `scripts/test_flow1.py` on Sarah Chen CRM record. **Trigger → Condition → Update = 3-node flow, 8-second end-to-end latency** (PATCH staging → flow fires → status flips back).

**Purpose:** When the AURUM matcher produces a high-confidence match (composite ≥ 0.85), automatically promote the staging record from MATCHED to SURVIVED state.

**AURUM stages exercised:** REFINE (auto-approval decision).

**Build-time scope reduction:** Originally spec'd action 3 was "Update canonical's `aurum_last_refined_date`". **Dropped during build** after discovering `aurum_last_refined_date` is a column on canonical (`aurum_customer`) only — adding it requires resolving the `aurum_canonical_customer` lookup on the trigger row to a canonical Row ID, which is a separate Get-a-Row + lookup-binding step. Three reasons for the drop:
1. The demo's visible narrative is the staging status flip — working
2. Audit is captured by Dataverse built-in `modifiedon` on the staging row
3. Time pressure — building action 3 now would block Flow 2 + Flow 3 builds

**Deferred (NOT a bug):** canonical `last_refined_date` sync as Phase 5 polish work. ROADMAP entry added.

### Trigger configuration

**Type:** Dataverse — "When a row is added, modified or deleted"

**One trigger configuration per staging table** = 3 separate flow instances OR 1 flow with 3 triggers in parallel branches. Recommended: **3 separate flows for clarity** (named Flow 1a CRM, Flow 1b ECOMM, Flow 1c LOYALTY), since per-table flows are easier to debug and modify independently.

For each staging table:
- **Change type:** Added or Modified
- **Table name:** (one of) `aurum_crm_customer`, `aurum_ecomm_customer`, `aurum_loyalty_customer`
- **Scope:** Organization
- **Select columns:** `aurum_match_confidence,aurum_processing_status,aurum_canonical_customer` (limits trigger noise — only fire when these specific columns change)
- **Filter rows (OData):**
  ```
  aurum_match_confidence ge 0.85 and aurum_processing_status eq 3
  ```
  (`3` = `MATCHED` per ProcessingStatus enum)

### Action sequence

1. **Condition** (sanity check): `aurum_canonical_customer` is not null. If null, terminate with "Skipped — no canonical link" reason. (Defensive: a record could be flagged MATCHED with no canonical due to upstream bug.)

2. **Update a row** (staging) — set:
   - `aurum_processing_status` = 4 (SURVIVED)

3. ~~**Update a row** (canonical, via `aurum_canonical_customer` lookup) — set: `aurum_last_refined_date = utcNow()`~~ **DROPPED during Phase 4 build** — see scope-reduction note at top of Flow 1 section. Phase 5 polish work.

4. **Terminate** with status = "Succeeded".

### Test scenarios (which demo records exercise this flow)

Demo records with composite ≥ 0.85 that trigger Flow 1:
- **Priya ECOMM** (composite=0.89) — auto-approve to canonical Priya Krishnamurthy
- **Priya LOYALTY** (composite=1.00) — auto-approve
- **Sarah CRM** (composite=1.00) — auto-approve to canonical Sarah Chen
- **Sarah ECOMM** (composite=0.85, name_boost_floor active) — boundary case; verifies `>= 0.85` includes 0.85
- **Aisha CRM** (composite=1.00) — auto-approve to canonical Aisha Mubarak
- **Aisha LOYALTY** (composite=1.00) — auto-approve

**Total demo records exercising Flow 1:** 6.

**To re-trigger for testing:** open one of these staging records in the model-driven app, modify any column (e.g., touch `aurum_loaded_date`), Save. The trigger fires on modification.

### Build steps in Power Automate maker UI

1. `make.powerautomate.com` → AURUM-PP-Dev → **+ Create** → **Automated cloud flow**
2. Flow name: `AURUM | REFINE | Auto-Approve | CRM` (one per table)
3. Trigger: search "Dataverse" → **When a row is added, modified or deleted**
4. Configure trigger (per "Trigger configuration" above)
5. Add condition step (per Action sequence step 1)
6. Add **Update a row** action (Dataverse) for staging — Row ID = trigger record ID, table = trigger entity
7. Add **Update a row** action for canonical — Row ID from `aurum_canonical_customer` lookup of trigger record, table = `aurum_customer`
8. Save → Test → run with the Priya LOYALTY record (highest confidence, easiest to verify)
9. Repeat steps 1–8 for ECOMM and LOYALTY tables (or clone Flow 1 CRM and edit trigger entity)

**Estimated time:** 15 min for first flow, 5 min each for ECOMM and LOYALTY clones = ~25 min total for Flow 1 (3 instances).

---

## Flow 2 — AURUM | REFINE | Steward Review Required

**Purpose:** When the matcher produces a borderline composite (0.55 ≤ confidence < 0.65), flag the staging record for steward review and (optionally) notify via Teams.

**AURUM stages exercised:** REFINE (escalation to human judgment).

### Trigger configuration

Same trigger pattern as Flow 1 (3 instances, one per staging table) — but with different filter:

- **Filter rows (OData):**
  ```
  aurum_match_confidence ge 0.55 and aurum_match_confidence lt 0.65 and aurum_processing_status eq 3
  ```
  (`3` = `MATCHED`. We catch records that scored above the candidate filter but below the auto-match threshold.)

### Action sequence

1. **Update a row** (staging) — set:
   - `aurum_processing_status` = 5 (STEWARD_REVIEW)

2. **Optional — Teams notification** (skip step if Teams connector unavailable):
   - **Microsoft Teams — Post message in a chat or channel**
   - Recipient: steward Teams channel (e.g., "AURUM Stewardship") OR direct chat to current steward user
   - Message body (suggested):
     ```
     🔍 Steward review needed
     Record: {triggerRecord_primary_name_field}
     Source: {triggerRecord_entity_logical_name}
     Match confidence: {aurum_match_confidence} (borderline band 0.55–0.65)
     Direct link: {model-driven app deep link to record}
     ```
   - Use dynamic content for `aurum_match_confidence` and the source-system label. Build the deep link using the env URL + entity set + record ID.

3. **Fallback if Teams blocked:** comment out the Teams step OR replace with a "Compose" action that just records the notification text into the flow run history (visible in flow run audit, satisfies the demo without external integration).

### Test scenarios

Demo records with 0.55 ≤ composite < 0.65 that trigger Flow 2:
- **Mohammed CRM** (composite=0.60, MatchMethod=FUZZY_BORDERLINE=3) — flag for review

**Total demo records exercising Flow 2:** 1 (the only borderline-band record in the demo data — by design, borderline cases are rare).

### Build steps

1. Same as Flow 1 build steps 1–4, but with Flow 2's filter
2. Add **Update a row** action (per Action sequence step 1)
3. Add **Microsoft Teams — Post message** OR fallback Compose (per step 2/3)
4. Save → Test → run with Mohammed CRM record (touch `aurum_loaded_date` to re-trigger)
5. Repeat for ECOMM and LOYALTY tables (no demo records will fire on those, but the flows must exist for production-readiness)

**Estimated time:** ~20 min for first flow (Teams setup adds time), ~5 min each for ECOMM/LOYALTY clones = ~30 min total for Flow 2 (3 instances).

---

## Flow 3 — AURUM | UNEARTH+MARK | Promote Unmatched to Canonical

**Purpose:** Steward-initiated promotion of an unmatched staging record into a new canonical record. Used when steward judges a "cold" prospect record represents a legitimate new customer.

**AURUM stages exercised:** UNEARTH (new entity creation from staging) + UNFURL (canonical materialization) + MARK (provenance via Dataverse audit).

### Trigger reformulation (Quirk 10 prevention)

User's verbal spec: `aurum_processing_status = UNMATCHED (6) AND a "Promote to Canonical" flag is set`. Issues:
- `aurum_processing_status` has no UNMATCHED value (value 6 is REJECTED)
- No "Promote to Canonical" flag column exists on staging tables

**Three reformulation options — pick one at build time:**

#### Option A (recommended) — manual instant trigger

**Type:** Dataverse — "When a row is selected" (instant cloud flow trigger)

- **Table name:** (one of) `aurum_crm_customer`, `aurum_ecomm_customer`, `aurum_loyalty_customer`
- Steward selects a record in the model-driven app's grid view, opens the **Flow** menu, clicks the flow → flow runs against that record
- **Pre-condition (in flow):** terminate if `aurum_canonical_customer` is not null OR `aurum_match_method` is not 5 (UNMATCHED) — defensive against accidental promotion of already-linked records

**Why recommended:** zero schema changes; clean steward UX; one explicit user action per promotion (auditability for free).

**Limitation:** "When a row is selected" triggers only one table per flow. So Flow 3 also becomes 3 sub-flows (Flow 3a CRM, Flow 3b ECOMM, Flow 3c LOYALTY).

#### Option B — automated trigger with new flag column

Add a new Yes/No column `aurum_steward_action_promote` to all 3 staging tables (deploy via `deploy_table.py`). Then trigger on:
```
aurum_steward_action_promote eq true and aurum_canonical_customer eq null
```

**Trade-off:** schema change required (1 column × 3 tables), but enables fully-declarative "set flag to trigger" flow. Slightly worse UX (steward edits a column instead of clicking a flow button).

#### Option C — model-driven app custom command bar button

Custom JavaScript-backed command on the staging entity grid that calls a custom action which then triggers the flow. **Defer — Phase 6 polish work, not Phase 4 scope.**

### Action sequence (assuming Option A)

1. **Pre-condition checks:**
   - If `aurum_canonical_customer` is not null → Terminate (Failed) with reason "Already linked to canonical"
   - If `aurum_match_method` ≠ 5 (UNMATCHED) → Terminate (Failed) with reason "Match method is not UNMATCHED — use steward review flow instead"

2. **Compute trust score (formula verified against public AURUM survivorship code):**

   **Source of truth:** `~/Projects/AURUM/refine/golden_record/survivorship.py:194-205`

   ```python
   key_fields = ["first_name", "last_name", "email", "phone", "city", "country"]   # 6 fields
   filled = sum(1 for f in key_fields if golden.get(f, "").strip())
   completeness = filled / len(key_fields)                  # 6 = denominator
   diversity    = min(len(distinct_sources) / 3, 1.0)       # cap at 3 sources
   trust_score  = round(0.6 * completeness + 0.4 * diversity, 2)
   is_golden    = trust_score >= 0.6                        # threshold = 0.60
   ```

   **For Flow 3 single-source promotion:**
   - `diversity` = 1/3 = 0.333... → contributes `0.4 × 0.333 = 0.133` to trust_score
   - For Hassan / Joana / Lukas / Maria (all 6 key fields populated in the demo data): `completeness = 6/6 = 1.0` → trust_score = `0.6 × 1.0 + 0.4 × 0.333 = 0.733` → **rounds to `0.73`**
   - With trust_score = 0.73 ≥ 0.60 threshold: **`is_golden = True`** (single-source promotions DO go golden if all 6 key fields are populated)

   **Power Fx pattern for Flow 3:**
   ```
   completeness:  Compose action — count non-empty key fields in trigger record / 6
                  (or hardcode 1.0 for the 4 demo prospects, which all have full key-field coverage)
   diversity:     Compose action — literal 0.333
   trust_score:   Compose action — Round(0.6 * completeness + 0.4 * diversity, 2)
   is_golden:     Compose action — trust_score >= 0.6  (boolean)
   ```

   **Demo records that exercise this:**
   - Hassan Bin Saeed (CRM): all 6 key fields populated → trust_score = 0.73, is_golden = True
   - Joana Reyes (CRM): all 6 key fields populated → trust_score = 0.73, is_golden = True
   - Lukas Weber (ECOMM): note ECOMM has shipping address fields, not the canonical address fields — when promoting from ECOMM, map shipping → address (city/country come from `aurum_default_shipping_*`). Same calc applies.
   - Maria L Santos (LOYALTY): note LOYALTY uses `_parsed` name fields. Same calc applies after mapping.

   **Replaces prior placeholder:** earlier draft used 0.83 / 0.33 / 0.63 — that was inferred without reading the actual survivorship code (Quirk-10-style spec invention). Corrected via direct citation 2026-05-03.

3. **Create a new row** in `aurum_customer` (canonical) — field mappings depend on source entity:

   **From CRM staging:**
   - `aurum_first_name` ← `aurum_first_name_raw`
   - `aurum_last_name` ← `aurum_last_name_raw`
   - `aurum_full_name` ← `concat(aurum_first_name_raw, ' ', aurum_last_name_raw)`
   - `aurum_email_primary` ← `aurum_email_raw`
   - `aurum_phone_primary` ← `aurum_phone_raw`
   - `aurum_address_line1` ← `aurum_address_line1_raw`
   - `aurum_city` ← `aurum_city_raw`
   - `aurum_country` ← `aurum_country_raw`
   - `aurum_crm_segment` ← `aurum_crm_segment` (carry through)
   - `aurum_lifetime_value` ← `aurum_crm_lifetime_value`
   - `aurum_completeness_score` = 0.83
   - `aurum_diversity_score` = 0.33
   - `aurum_trust_score` = 0.63
   - `aurum_is_golden` = false (single-source promotions don't auto-golden)
   - `aurum_source_systems` = `"CRM"`
   - `aurum_first_seen_date` = `aurum_loaded_date` (carry through)
   - `aurum_last_refined_date` = `utcNow()`
   - `aurum_steward_review_status` = 1 (AUTO_APPROVED — steward initiated the promotion, so it's pre-approved)

   **From ECOMM staging:** same pattern, but use shipping address fields (`aurum_default_shipping_*` → canonical address), and `aurum_source_systems = "ECOMM"`.

   **From LOYALTY staging:** use `_parsed` name fields, copy `aurum_loyalty_member_number` + `aurum_loyalty_tier` + `aurum_loyalty_points_balance` + `aurum_loyalty_member_since` + `aurum_birth_year`, `aurum_source_systems = "LOYALTY"`.

4. **Update a row** (staging) — set:
   - `aurum_canonical_customer` = (newly-created canonical record's ID, captured from step 3 output)
   - `aurum_processing_status` = 4 (SURVIVED)
   - `aurum_match_method` = 6 (SINGLE_SOURCE_PROMOTION) — only valid on LOYALTY per matcher; for CRM/ECOMM use STEWARD_APPROVED=4 instead. Per-source enum gate at action-config time.

5. **Terminate** with status = "Succeeded" + reason = "Promoted staging record to new canonical"

### Test scenarios

Demo records that exercise Flow 3:
- **Hassan Bin Saeed** (CRM prospect, composite=0.0, no canonical link) — single-source promotion to new canonical
- **Joana Reyes** (CRM prospect) — same
- **Lukas Weber** (ECOMM prospect) — single-source promotion (uses ECOMM action mapping)
- **Maria L Santos** (LOYALTY prospect) — single-source promotion (uses LOYALTY action mapping; SINGLE_SOURCE_PROMOTION=6 valid here)
- **Priya CRM** (composite=0.51, below candidate filter, manually linked in demo) — edge case: this record IS already linked to canonical, so Option A's pre-condition would terminate the flow. Demonstrates the safety check works.

**Total demo records exercising Flow 3:** 4 prospects (5 if you count the Priya CRM negative-test case).

### Build steps

1. `make.powerautomate.com` → AURUM-PP-Dev → **+ Create** → **Instant cloud flow**
2. Flow name: `AURUM | UNEARTH+MARK | Promote to Canonical | CRM`
3. Trigger: search "Dataverse" → **When a row is selected** → table = `aurum_crm_customer`
4. Add condition steps (per Action sequence step 1)
5. Add Compose actions for trust score variables (per step 2)
6. Add **Add a new row** (Dataverse) for canonical — table = `aurum_customer` (per step 3 mapping)
7. Add **Update a row** (Dataverse) for staging (per step 4) — capture canonical ID from step 6 output
8. Save → Test → manually run on a prospect record (e.g., Hassan Bin Saeed)
9. Verify in model-driven app: new canonical exists, staging record now links to it, processing_status changed
10. Repeat steps 1–9 for ECOMM and LOYALTY tables (with per-source field mappings)

**Estimated time:** ~30 min for first flow (action mapping is verbose), ~15 min each for ECOMM and LOYALTY = ~60 min total for Flow 3 (3 instances).

---

## Total Phase 4 build estimate

- Flow 1 (3 instances): ~25 min
- Flow 2 (3 instances): ~30 min
- Flow 3 (3 instances): ~60 min
- **Total: ~115 min (~2 hours) of maker UI work** — fits the 5:00 PM session.

---

## Architect's brief

### Why three flows, not one mega-flow

Each flow has a distinct trigger condition, distinct action sequence, and distinct ownership of failure modes. A mega-flow with branched logic would:
- Require complex condition trees that re-implement what trigger filters do natively
- Mix unrelated failure modes (a Teams API timeout in the borderline path would fail-stop the auto-approve path)
- Be harder to reason about, debug, and modify independently
- Scale poorly when Phase 5+ adds Flow 4 (rejection handling), Flow 5 (re-match on staging update), etc.

Per-flow separation is the standard Power Automate pattern for this kind of event-driven enrichment work, and matches how `load_sample_data.py` has separate scoring + survivorship + promotion concerns.

The **3 instances per flow** (one per staging table) is a Power Automate trigger limitation — the "When a row is added, modified or deleted" trigger binds to ONE table per flow. Could collapse via 3 parallel branches in a single flow keyed off entity name, but the cost (cross-source debugging when one branch fails, harder per-flow audit history) outweighs the benefit (one less flow card on the maker home page). Per-source flows match per-source views in the sitemap — consistent mental model.

### Trigger choice rationale: row-modified vs scheduled

**Row-modified wins:**
- Near-real-time response (typically <30s end-to-end on Power Platform)
- Cleaner audit trail — each flow run pairs with a specific row update event, preserves causality
- Native filter expression support (OData) means trigger condition is enforced at the platform level, not in flow logic — cheaper + more reliable
- Scales without scheduling-window tuning

**Scheduled would be needed only if:**
- We had no row-modify hook (we do)
- We needed batch-mode reprocessing (e.g., re-score all records nightly when matcher version updates) — Phase 5+ could add a scheduled flow alongside the row-trigger flows

For Phase 4's REFINE/UNFURL/MARK demonstration, row-modified is the right primitive. Steward sees a record's processing_status change within seconds of the matcher emitting the score.

### What demo records exercise each flow path

Coverage across the 96 demo records:

| Flow | Composite range | Demo records that trigger | Count |
|---|---|---|---:|
| Flow 1 (auto-approve) | ≥ 0.85 | Priya ECOMM (0.89), Priya LOYALTY (1.00), Sarah CRM (1.00), Sarah ECOMM (0.85), Aisha CRM (1.00), Aisha LOYALTY (1.00) | 6 |
| Flow 2 (steward review) | 0.55–0.65 | Mohammed CRM (0.60) | 1 |
| Flow 3 (promote unmatched) | < 0.55 (cold) OR demo override | Hassan Bin Saeed, Joana Reyes, Lukas Weber, Maria L Santos (4 prospects) | 4 |
| (none) | 0.65–0.85 | (no demo records in this band) | 0 |
| (none — handled in demo by manual link) | < 0.55 manually linked | Priya CRM (0.51) — REFINE skipped, demo override illustrates UNEARTH dependency | 1 |

**Coverage gap discussion:** The 0.65–0.85 band has no flow handler. Records there land in MATCHED state and stay there until either (a) re-scored to a higher confidence by an updated matcher, or (b) manually escalated to STEWARD_REVIEW via the views. **This is intentional for Phase 4** — these are "matched, not auto-approved" records that the demo narrative doesn't need to animate. Phase 5 could add a Flow 1.5 to bulk-promote 0.65-0.85 records to a steward queue if the pipeline volume warrants it. For Phase 4, the views handle this state visually.

### MARK stage — what we're NOT building

User's verbal spec acknowledged the MARK stage audit table doesn't exist. Decision: lean on **Dataverse's built-in audit log** for Phase 4. Every row update from Flows 1–3 is captured automatically (table-level audit ON, project convention). Steward can view audit history per-record in the model-driven app's "Audit history" related view.

A custom `aurum_mark_lineage_event` table (with columns like `event_type`, `source_record`, `target_record`, `actor`, `confidence_at_event`, `flow_run_id`) is documented in ROADMAP.md as deferred — adds a sixth table, would need its own deploy, and the demo doesn't depend on cross-flow event correlation that built-in audit can't cover.

**Trigger to revisit:** when a regulatory/compliance ask requires "show me every time this customer record was modified, by which flow, with what confidence value at that moment." Built-in audit doesn't capture confidence-at-event semantically — only the value-after-update. Custom MARK table is the right answer when this becomes load-bearing.

---

## Out of scope today — Anti-match rule for conflicting discriminators (Phase 5+)

**Design intent (locked 2026-05-03):** When two records have a strong name match but different phone numbers, the pair should NOT auto-approve to SURVIVED regardless of composite score — they must route to STEWARD_REVIEW. Discriminator conflict on a contact channel is suspicious enough to warrant human judgment even when the matcher's composite score says "confident match."

### Why this is out of scope for Phase 4

1. **Zero current demo coverage.** All 6 high-confidence (≥0.85 composite) demo records have phone numbers that are IDENTICAL between staging and canonical (Priya, Sarah, Aisha — all six pairs verified 2026-05-03). The rule would fire on no demo records under current sample data. Building flow infrastructure for an un-exercised rule violates "ship working tools."

2. **Architectural fit.** Anti-match logic IS matching logic — it determines what counts as a confident match. It belongs in the AURUM matcher (`refine/matching/matcher.py`), not in Power Automate workflow orchestration. Putting it at flow level would emit contradictory signals (matcher says `match_method = FUZZY_HIGH`, flow says "route to steward review") that downstream consumers have to reconcile.

3. **Single source of truth for phone normalization.** The matcher already normalizes phones for `phone_score` calc (`"".join(c for c in phone if c.isdigit())[-9:]`, lines 77-79 of public AURUM `matcher.py`). A flow-level rule would need to re-implement this in Power Fx — two implementations = two divergence points = drift risk.

4. **Flow mechanics cost.** Power Automate trigger filters work on trigger-entity columns only (OData). Anti-match check would require a post-trigger Get-a-Row of the canonical + Condition step with Power Fx normalization expression + branched paths. Doubles Dataverse calls per Flow 1 run, for a rule that currently fires on no demo records.

### Phase 5 work scope (when this gets built)

**AURUM repo (`~/Projects/AURUM/`):**
- Add anti-match check after composite calc in `score_pair()` (~10 LOC).
- Decide signal mechanism: either (a) new field on `MatchCandidate` like `discriminator_conflict: bool` that callers can inspect, or (b) new `MatchMethod` value `ANTI_MATCH_DISCRIMINATOR_CONFLICT = 7` that overrides the FUZZY_HIGH/EXACT classification when fired.
- Recommend (a) — keeps the composite/method classification orthogonal to the conflict signal; downstream code can decide policy.
- Bump AURUM version to v0.3.0.

**AURUM-PP:**
- Regenerate sample data with one demo record exercising the rule. Concrete suggestion: "Sarah Chen Dubai" — same name as canonical Sarah, same email, but different phone (e.g., `+971-50-XXX-XXXX` swapped to a different number). Should land at composite ≥0.85 via name_boost_floor (name=1.0, email=1.0, phone=0 → weighted=0.90, floor=0.85, composite=0.90), then `discriminator_conflict=true` flag flips processing_status to STEWARD_REVIEW.
- Bump `AURUM_PP_AURUM_COMMIT_PIN` to the v0.3.0 commit hash.
- Regenerate `docs/demo_records_aurum_lineage.md` to document the new demo + the rule.

**Flow layer:**
- Flow 1 stays simple — its OData filter `aurum_match_confidence ge 0.85 and aurum_processing_status eq 3 (MATCHED)` already excludes records the matcher set to STEWARD_REVIEW upstream.
- Flow 2 (steward review) picks up the new state via its existing filter, OR extend Flow 2's filter to also catch `aurum_processing_status = 5 AND aurum_match_method = 7` (if option (b) was chosen above).

**Trigger to revisit before Phase 5:**
- Confirm Sarah Chen demo regeneration won't break the "Multi-Brand Sarah" narrative (`#AURUM-NameBoostFloor` tag). The current Sarah ECOMM at 0.85 is the textbook boost-floor demo. Adding a "Sarah Chen Dubai" anti-match demo augments rather than replaces.

### Audit summary (verifications run 2026-05-03 before deferring)

| Check | Finding |
|---|---|
| High-conf demo records phone-aligned? | 6/6 ✓ identical |
| Sarah Chen demo broken by rule? | No |
| Aisha Mubarak linked-tuple demo broken by rule? | No |
| Phone storage format uniform? | Yes (`+971-XX-XXX-XXXX` across all good data; malformed cases <10% of filler stagings only) |
| Matcher normalization reliable? | Yes — last-9-digits-of-digit-stripped-string |
| Flow-level normalization feasible? | Yes but verbose Power Fx; would diverge from matcher's normalization |

---

## Open questions / decisions deferred

All four prior open questions are now LOCKED — see "Locked decisions" table at top of doc. Section retained as historical record:

1. ~~Flow 3 trigger choice (A vs B)~~ → **Locked: Option A (manual instant trigger)**
2. ~~Flow 2 Teams notification: include or skip~~ → **Locked: SKIP for tonight**
3. ~~Per-record vs constant trust-score completeness~~ → **Locked: verified formula from public AURUM survivorship code; trust_score=0.73 for the 4 demo prospects**
4. ~~Flow 3 instance count~~ → **Scope reduced: CRM-only tonight (1 Flow 3 instance, not 3). ECOMM/LOYALTY = Phase 5.**

---

## Stop conditions / when to escalate to me during build

Per Phase 3 support pattern, escalate during the maker UI build when you hit:
- An OData filter expression that the trigger config rejects (might be syntax — I can check the expression)
- A field name that's not selectable in dynamic content (Quirk 4 territory — auto-companion column, virtual field)
- A trust-score expression in Flow 3 that doesn't compile (Power Fx vs OData expression confusion)
- Any "this connector requires admin approval" prompt (DLP policy issue, not just sign-in)
- After each Flow saves successfully — Web API verification that the workflow record exists with `statecode=Activated`
