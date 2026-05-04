# Cowork handoff prompt — AURUM-PP technical layout doc

Paste this entire document to Cowork to generate the comprehensive
technical layout for AURUM-PP.

---

You are Cowork, picking up the AURUM-PP project from a previous 
Claude Code session. Working directory is 
~/Projects/AURUM/power-platform/.

TASK: Write a comprehensive technical layout document for AURUM-PP 
that Raja Shahnawaz Soni will use to brief colleagues at work and 
teach students. Single document, deeply detailed, defensible.

============================================================
PRE-WORK (5 min) — load context before writing
============================================================

Read in this order:
  1. CHANGELOG.md — chronological build history
  2. ROADMAP.md — what's done, what's next, what's deferred
  3. DEFENSE_BRIEF.md — talking points and defensible claims
  4. README.md — public-facing summary
  5. docs/TOMORROW_TECHNICAL_TOUCHPOINT.md — skeleton outline 
     from previous session (this is the scaffold to expand)
  6. docs/phase4_flow_specifications.md — Flow 1, 2, 3 specs
  7. docs/phase4_anti_match_audit.md — why anti-match was deferred
  8. docs/dataverse_quirks.md (or similar) — 11 Dataverse quirks
  9. dataverse-schemas/*.yaml — what was actually deployed
 10. scripts/auth.py, scripts/deploy_table.py, 
     scripts/load_sample_data.py — IaC entry points
 11. ../assay/, ../unearth/, ../refine/, ../unfurl/, ../mark/ — 
     parent AURUM repo Python modules (read at least __init__.py 
     and one matcher file like refine/matching/matcher.py)

If any file is missing, report it. Don't invent content for 
files you can't read. Same Reality Auditor stance Raja has 
used throughout — guilty until proven otherwise.

============================================================
DOCUMENT TO WRITE
============================================================

File path: power-platform/docs/AURUM_PP_TECHNICAL_LAYOUT.md

Audience: TWO simultaneous audiences
  - Work colleagues (data architects, MDM practitioners, 
    Power Platform engineers) who need defensible technical 
    detail
  - Students (data engineering / MDM learners) who need 
    architectural framing and the "why" behind decisions

Length target: 3000-4500 words. Deep enough to be authoritative, 
focused enough to be readable in one sitting.

Tone: Direct, practitioner-voice, honest about gaps. No marketing 
language. No "transformative innovation" claims. Match the 
DEFENSE_BRIEF voice Raja has been using.

Structure:

  # AURUM-PP — Technical Layout
  
  Top header: short summary, 2 sentences max. What it is, what 
  it demonstrates.
  
  ## 1. Project context
  - The AURUM open-source repo (github.com/RajaMDM/AURUM): 
    what it is, what it provides, why it exists
  - AURUM-PP as the Power Platform implementation: 
    parent-child relationship, monorepo structure
  - The mechanical lineage: AURUM-PP imports the matcher from 
    AURUM at runtime (not vendored). Cite the import path 
    (refine.matching.matcher) and the commit hash (78223b6)
  - Why this matters: vendor-neutral architecture proven by 
    code dependency, not just claim
  
  ## 2. Five-stage AURUM architecture mapped to Power Platform
  
  For EACH of ASSAY, UNEARTH, REFINE, UNFURL, MARK:
  - 1-line stage purpose (from parent AURUM repo)
  - What Power Platform component implements it in AURUM-PP
  - Concrete artifact reference (Dataverse table name, flow 
    name, file path)
  - Status (deployed / partial / deferred)
  
  Use a table for this mapping. Include both the canonical 
  AURUM stage AND the Power Platform realization side-by-side.
  
  ## 3. Deployed components inventory
  
  ### 3.1 Dataverse schema (5 tables)
  For each table:
  - Logical name (e.g., aurum_customer)
  - Display name
  - Purpose (which AURUM stage(s) it serves)
  - Record count (canonical 30, CRM 23, ECOMM 20, LOYALTY 15, 
    ASSAY 8 — verify by reading sample data scripts)
  - Notable architectural decisions (PK convention, primary 
    name field choice, calculated fields, etc.)
  
  Cite specific YAML files in dataverse-schemas/ for verification.
  
  ### 3.2 Sample data
  - Total records: 96
  - Hero records: Sarah Chen, Mohammed Al-Rashid, Priya 
    Krishnamurthy, Aisha Mubarak, Hassan Bin Saeed, Joana Reyes 
    — what each demonstrates architecturally
  - Real AURUM matcher integration: the matcher is imported 
    from parent repo, NOT vendored or reimplemented. Cite 
    score_pair() function, weights (name 0.65, email 0.25, 
    phone 0.10), name_boost_floor logic.
  - The hallucination catch: yesterday the agent invented 
    scoring components ("phone-cluster", "region-similarity") 
    that don't exist in the real matcher. Caught via Reality 
    Auditor stance, corrected by reading actual source code. 
    This is a teaching moment — surface it.
  
  ### 3.3 Model-driven app: AURUM Steward Workbench
  - Status: published, On
  - 5 table pages
  - 3 custom views (Pending Steward Review on CRM/ECOMM/LOYALTY)
  - Honest gap: sitemap reorganization into AURUM stage groups 
    deferred (maker UI bug — drag-drop didn't expose group 
    create/move). Phase 5 polish.
  
  Document each Pending Steward Review view's filter and sort:
    - Filter: aurum_processing_status = STEWARD_REVIEW (5)
    - Sort: aurum_match_confidence ascending (lowest first)
    - Columns: source-specific value indicator (LTV for CRM, 
      Total Spend for ECOMM, Tier for LOYALTY)
  
  Steward queue contents at end of build:
    - CRM: 4 records (Priya 0.51, Mohammed 0.60, Andrea 0.71, 
      Tao 0.71)
    - ECOMM: 2 records (both 0.69)
    - LOYALTY: 3 records (Yusuf 0.69, Marco 0.71, Andrea 0.79)
  
  ### 3.4 Power Automate flows
  
  For Flow 1 and Flow 2 (Flow 3 deferred):
  - Full name, trigger, condition logic, action
  - Test subject and verification result
  - Latency observed (Flow 1: 8s, Flow 2: 24s)
  
  Honest framing: Flow 3 (Promote Unmatched to Canonical) NOT 
  built yet. Different architectural shape (manual instant 
  trigger, create-row, multi-field map, lookup relink). 
  Deferred for architectural correctness, not skipped.
  
  ## 4. Touchpoints with the AURUM GitHub repo
  
  This is the MOST IMPORTANT section for the "vendor-neutral 
  architecture" defense. Document every concrete dependency 
  AURUM-PP has on the public AURUM repo:
  
  - Matcher import (refine.matching.matcher.score_pair) — used 
    by load_sample_data.py at runtime to compute composite 
    scores for sample records. Show the import statement.
  - Trust score formula citation 
    (refine.golden_record.survivorship.trust_score, lines 
    194-205) — used to verify Flow 3's expected canonical 
    trust score (0.73). Cite the formula: 0.6 × completeness 
    + 0.4 × diversity.
  - Stage architecture pattern (5-stage ASSAY → UNEARTH → 
    REFINE → UNFURL → MARK) — adopted from AURUM, not 
    invented for Power Platform.
  - Enum value source-of-truth — ProcessingStatus, MatchMethod, 
    AssaySeverity — all defined in load_sample_data.py and 
    cross-referenced when building flow conditions. Critical 
    for Quirk-10 prevention.
  
  Why this matters narrative: anyone could build "an MDM thing" 
  on Power Platform. AURUM-PP is specifically positioned as 
  THE Power Platform realization of the AURUM vendor-neutral 
  reference architecture. The mechanical dependency is the 
  proof.
  
  ## 5. Infrastructure as Code posture (honest framing)
  
  ### What IS IaC
  - Dataverse schema deployment: 100% scripted via 
    deploy_table.py + YAML
  - Sample data load: 100% scripted via load_sample_data.py
  - Authentication: env-var-driven, MSAL-based, no hardcoded 
    credentials
  - Verification: scripted via verify_env_columns.py and 
    test_flow*.py
  
  ### What is NOT yet IaC
  - Model-driven app: built in maker UI
  - Custom views: built in maker UI  
  - Cloud flows: built in maker UI
  
  ### Migration path (Phase 5+)
  Solution-export pipeline using Microsoft-documented ALM 
  patterns. Cite: 60-90 min upfront cost, then ~5 min per 
  additional flow. Trigger to revisit: when ECOMM/LOYALTY 
  flow replication justifies the upfront work.
  
  ### Why this honest framing matters
  Overclaiming "fully IaC" damages credibility when reviewed 
  by a colleague who knows the maker UI was used. "Hybrid IaC 
  with documented migration path" is defensible, accurate, 
  and tells a maturity-ladder story that enterprise Power 
  Platform shops recognize.
  
  ## 6. Reality Auditor moments (teaching value)
  
  This section is GOLD for the student audience. Surface the 
  actual self-correction events from the build log:
  
  - The matcher hallucination catch (Day 2 morning): agent 
    invented scoring components to justify hand-picked numbers. 
    Caught by reading actual source code. Corrected lineage doc.
  - The trust score invention catch (Day 2 evening): agent 
    cited 0.63 as canonical trust score for single-source 
    promotions. Caught when verifying against survivorship.py. 
    Real value 0.73, with is_golden=True (opposite of agent's 
    earlier claim). 
  - The Quirk-10 enum conflation (Day 2 evening): user said 
    "Flow 3 trigger: aurum_processing_status = UNMATCHED (6)". 
    Agent caught: ProcessingStatus has no UNMATCHED value; 
    value 6 is REJECTED. UNMATCHED lives in MatchMethod enum.
  - The undocumented POST /workflows path (Day 3 morning): 
    agent investigated programmatic flow deployment, hit 
    undocumented Microsoft API surface, reported clean and 
    stopped per user's "fall back to maker UI if blocked" rule.
  - The DEFENSE_BRIEF scope creep (Day 3 morning): agent 
    added an extra paragraph beyond user's verbatim spec, 
    self-corrected and reverted.
  
  Frame each as: what was tempting to do wrong, what the 
  Reality Auditor stance demanded instead, and what was 
  learned.
  
  ## 7. Open risks and gaps
  
  Be exhaustive and honest. Don't soften.
  
  - Form auto-generation insufficient for steward UX (Phase 5 
    custom forms work)
  - Sitemap reorganization deferred (maker UI quirk)
  - Flow 3 not yet built
  - ECOMM and LOYALTY flow replication not done (6 more flows)
  - Anti-match rule for conflicting discriminators (deferred 
    to AURUM v0.3.0 — cross-repo work)
  - Power Automate trigger latency dependency (8-24s observed, 
    not contractually guaranteed by Microsoft)
  - DLP policies could block flows in stricter envs
  - Choice field integer-vs-label coupling (Quirk 10 surface 
    that bites at every flow build)
  - last_refined_date sync between staging and canonical 
    deferred (lookup resolution complexity in Flow 1)
  - No PII handling for production data — current sample data 
    is synthetic (Phase 5 work)
  - No multi-tenant isolation tested
  - Connection reference dependency: every flow imports 
    aurum_sharedcommondataserviceforapps_8e3b2 — environment 
    promotion requires connection re-binding
  
  ## 8. Reliability and trust plan
  
  How AURUM-PP becomes production-grade:
  
  - Dataverse audit log captures every flow modification 
    (already enabled by default)
  - Source-of-truth verified enums (load_sample_data.py as 
    canonical) — pattern documented in 
    feedback_spec_enum_source_of_truth.md memory
  - Web API testing harness (test_flow1.py, test_flow2.py 
    pattern) — every flow gets a regression test before 
    activation
  - Phased flow buildout with one-flow-at-a-time validation
  - Public AURUM repo as the dependency source — vendor-neutral 
    matcher logic, not Microsoft-specific reimplementation
  - Solution-export pipeline (Phase 5) closes the IaC gap
  - Anti-match rules in AURUM v0.3.0 close the conflicting-
    discriminator gap
  - Documentation discipline: PROJECT_HISTORY.md, 
    TECH_MEMORY.md, CHANGELOG.md, DEFENSE_BRIEF.md, ROADMAP.md 
    — every project has all five
  
  ## 9. Demo narrative arcs (for live presentation)
  
  Three scenarios stewards see:
  
  ### Scenario 1: Auto-approval (Sarah Chen)
  - Sarah's CRM record has match_confidence = 1.00
  - Flow 1 fires within 8 seconds of any status change
  - Status flips MATCHED (3) → SURVIVED (4)
  - Steward sees nothing — handled automatically
  
  ### Scenario 2: Steward review (Mohammed Al-Rashid)
  - Mohammed's CRM record has match_confidence = 0.60 
    (borderline band)
  - Flow 2 routes to STEWARD_REVIEW within 24 seconds
  - Mohammed appears in CRM Pending Steward Review queue
  - Steward exercises judgment
  
  ### Scenario 3: Promote unmatched (Hassan Bin Saeed) — 
  PENDING Flow 3
  - Hassan has no canonical match
  - Steward selects Hassan and clicks "Promote to Canonical"
  - Flow 3 creates new canonical record with trust 0.73, 
    is_golden=True, links staging → canonical
  
  ## 10. What's next
  
  Day 4 priorities:
  - Build Flow 3 (~45-60 min)
  - Capture screenshots of all 3 flows
  - Optional: ECOMM/LOYALTY replication via Phase 5 
    solution-export pipeline
  
  Phase 5 priorities:
  - Form customization
  - Sitemap reorganization
  - Solution-export IaC pipeline
  - Anti-match rule (cross-repo to AURUM v0.3.0)
  
  ## 11. References
  
  - Public AURUM repo: github.com/RajaMDM/AURUM
  - AURUM-PP within AURUM: 
    github.com/RajaMDM/AURUM/tree/main/power-platform
  - LinkedIn: linkedin.com/in/raja-shahnawaz/
  - Built by: Raja Shahnawaz Soni (architect), Claude Code 
    (build agent), Cowork (this doc)
  
============================================================
QUALITY BAR
============================================================

Before declaring done, verify:

  - Every component claim has a file path or schema reference
  - Every flow latency claim cites the test that produced it
  - Every "deferred" item has a "why" and a "trigger to revisit"
  - Every AURUM repo touchpoint cites the specific module / 
    function / line number
  - No invented features (Quirk-10 stance — guilty until proven)
  - No marketing language ("transformative", "revolutionary", 
    "next-gen", "leveraging", "unlocking") — Reality Auditor 
    voice throughout
  - Two-audience adaptation visible: technical depth for 
    work colleagues, architectural "why" for students

If you can't verify a claim from the file system, mark it 
"PENDING VERIFICATION" rather than asserting.

============================================================
SCREENSHOTS GUIDANCE
============================================================

Don't generate or describe images. Leave placeholder lines:

  > [SCREENSHOT: Cloud flows list showing both flows ON]
  > [SCREENSHOT: Sarah Chen CRM record post-Flow-1 auto-approve]
  > [SCREENSHOT: Pending Steward Review queue with Mohammed]
  
Raja captures these manually before presenting.

============================================================
FINAL CHECK
============================================================

After writing, run a self-audit:
  - Read the doc top-to-bottom as if you're a colleague who 
    has never seen AURUM-PP
  - Flag any section that's hard to follow without already 
    knowing the project
  - Flag any claim that sounds defensive instead of confident
  - Flag any place where the AURUM-AURUM-PP relationship is 
    unclear

Report flagged items at the end of the agent response. Don't 
auto-fix — surface them for Raja to review.

After report, stop. No further work.
