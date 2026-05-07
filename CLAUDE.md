# AURUM — Project Context for Claude Code

## What This Project Is
Vendor-agnostic Master Data Management (MDM) reference implementation.
"Raw data in. Hallmarked golden records out."
Version: v0.1.3 | Language: Python 3.12 | License: MIT

## Five Pipeline Stages
- ASSAY (01)   — Ingestion, schema mapping, migration
- UNEARTH (02) — Profiling, DQ rules, anomaly detection
- REFINE (03)  — Matching, mastering, golden record assembly
- UNFURL (04)  — Publication, APIs, subscriptions
- MARK (05)    — Reverse integration, lineage, reconciliation

## Seven Domains
Customer, Product, Vendor, Asset, Location, Employee, Counterparty

## Runtimes
- CLI (click + rich)
- FastAPI HTTP (v0.1.3)
- MCP server (3 tools: assay_schema, unearth_profile, refine_match)

## Key Tech
- Isolation Forest anomaly detector
- LLM rule generator (Anthropic SDK)
- RapidFuzz + Jaro-Winkler matching
- Python venv — activate with: source venv/bin/activate

## Key Commands
- python demo/end_to_end_demo.py   — full pipeline demo
- python shared/sample_data/generate_all.py — generate sample data
- pip install -r requirements.txt — install deps

## Related Projects
- AURUM-PP (~/Projects/AURUM-PP) — Power Platform companion, imports AURUM matcher directly
- BMAD project: ~/Projects/BMAD — documentation and planning agents
  - Mary (Analyst), Paige (Tech Writer), John (PM), Sally (UX), Winston (Architect), Amelia (Dev)
  - Config: ~/Projects/BMAD/_bmad/config.toml
  - Outputs go to: ~/Projects/BMAD/_bmad-output/

## gstack Skills Available
Use these slash commands for all major workflow tasks:
- /office-hours       — strategic product thinking (start here for new features)
- /plan-ceo-review    — product/strategy review before building
- /plan-eng-review    — architecture + technical review
- /plan-design-review — UX/design review
- /review             — code review on current branch before merging
- /ship               — prepare and ship a PR
- /qa                 — full QA pass (opens browser if needed)
- /qa-only            — QA without shipping
- /investigate        — deep dive into a bug or issue
- /autoplan           — auto-generate an implementation plan
- /cso                — OWASP + STRIDE security audit
- /retro              — post-release retrospective
- /document-release   — generate release documentation
- /guard              — lock a file/section from AI edits
- /freeze / /unfreeze — protect stable code from changes
- /canary             — canary deploy check
- /browse             — use for all web browsing (never use mcp__claude-in-chrome__* tools)

## Workflow: New Feature
1. /office-hours — describe the feature idea
2. /plan-eng-review — validate architecture
3. /autoplan — generate implementation plan
4. Implement
5. /review — code review
6. /qa — quality check
7. /ship — PR and release

## Living Documents (always keep updated)
- PROJECT_HISTORY.md — business narrative of what was built and why
- TECH_MEMORY.md — technical decisions, architecture rationale, known gotchas
- CHANGELOG.md — significant changes with date, what, why, business impact
- ROADMAP.md — what comes next
