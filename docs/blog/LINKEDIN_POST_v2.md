# LinkedIn Post — v2 (AI Stack Angle)
# "Running an Enterprise MDM Project From My Phone"
# Raja Shahnawaz Soni

---

**I'm running a full enterprise MDM project from my phone.**

No laptop open. No IDE. No meetings. Just Telegram and an AI team that never clocks out.

Let me show you what that actually looks like.

---

**The stack:**

→ **Hermes** (AI team lead) — lives on my dev machine, listens on Telegram 24/7, has memory across every session, can schedule tasks, push code, cut releases, and deliver files straight to my phone

→ **BMAD** — 14 specialist AI agents, each with a name, a role, and a domain. Shazia runs DQ. Inaayah writes documentation. Nadia owns governance. Tariq handles compliance. Pierre does architecture. When I say "Inaayah, draft the compliance section" — she drafts it.

→ **gstack** (90k ⭐ on GitHub) — 23 engineering workflow slash commands wired directly into the project. `/office-hours` before I build anything. `/review` before I commit. `/ship` to push and open the PR. `/retro` after release.

→ **Claude Code** — the execution engine. Writes files, runs terminals, calls git, patches code, reads the whole codebase. The hands of the operation.

→ **Telegram** — the only interface I need. Feature requests go in. Code, commits, CI results, and release confirmations come out.

---

**What this looked like this morning:**

> **6:30 AM.** I message Hermes: *"Morning. Let's sort the GitHub CI failures and cut the v0.2.0 release."*

Hermes checks CI — 3 failures, root cause identified in seconds. Demo was hardcoded to 50 rows; our dataset is now 3,000. 2-line fix. Patched, tested locally, committed.

Then: version bump across README, CHANGELOG, CITATION.cff. Tag created. GitHub release cut. Badge updated. All delivered back to my Telegram as a confirmation.

**Total time: under 90 minutes.**
**Meetings: 0.**
**Laptop: closed.**

---

**What we shipped in v0.2.0 of AURUM:**

AURUM is my open-source MDM reference implementation — vendor-agnostic, Python, MIT licence.

This release:
- **3,000 rows** of dirty synthetic data across all 7 MDM domains (Customer, Product, Vendor, Asset, Location, Employee, Counterparty) — globally diverse, not just GCC
- **41 real-world MDM scenario playbooks** — single domain → cross-domain pairs → one grand scenario where all 7 domains cascade from a single business event (new store opening)
- **"The Intelligent Refinery"** — a narrative doc on what MDM looks like when AI enters the pipeline. LLM rule generation. Isolation Forest anomaly detection. MCP-native pipeline. Agentic stewardship.
- **Global data sovereignty guide** — AURUM mapped to UAE PDPL, ADDA (Abu Dhabi), DDA (Dubai), KSA PDPL + NDMO, Qatar PDPL, GDPR, CCPA, India DPDP, China PIPL, and 10+ more frameworks. Official public links for every one.
- **Disclaimer** — all company names fictional, any resemblance coincidental.

---

**The honest version of this story:**

I have 20 years in enterprise data. I know what it costs to run an MDM programme the traditional way — the headcount, the vendors, the timelines, the meetings about the meetings.

AURUM is my answer to the question: *what does MDM look like if you build it right, today, with the tools available today?*

The pipeline is ASSAY → UNEARTH → REFINE → UNFURL → MARK. Named for metallurgy — gold starts as ore, not as a bar. MDM is the refinery.

The AI team doesn't replace the data practitioner. It removes the friction between what the practitioner knows and what gets built. I make the decisions. The stack handles execution.

Three runtimes: CLI, FastAPI, and MCP server — so any AI agent (Claude, Cursor, Copilot) can call the MDM pipeline as a native tool, mid-conversation, without a pre-built integration.

---

**The repo:** github.com/RajaMDM/AURUM

The how-we-build doc is in there too — full breakdown of the Hermes + BMAD + gstack + Claude Code + Telegram stack, with the exact workflow.

If you're building anything with this kind of AI-native workflow — or if you're an MDM practitioner who's tired of the old way — I'd love to hear from you.

---

*Raw data in. Hallmarked golden records out.*
*Now with a team that never sleeps, run from a phone.*

---

**#MDM #MasterDataManagement #AI #AgenticAI #DataGovernance #OpenSource #Python #MCP #ClaudeCode #BMAD #gstack #Hermes #DataQuality #BuildInPublic**

---
> Draft saved: 2026-05-07
> Status: Ready for Raja's review before posting
> Word count: ~620
> Note: Post the GitHub link in first comment (not body) for max LinkedIn reach
