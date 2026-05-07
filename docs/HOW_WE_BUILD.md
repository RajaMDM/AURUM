# How We Build AURUM
### Running an Enterprise MDM Project From Your Phone With an AI Team

> *A practitioner's guide to the stack behind AURUM — tools, agents, and the workflow*

---

## The Setup in One Sentence

A 20-year enterprise data veteran runs a production-grade MDM reference implementation — architecture, code, documentation, releases, compliance — entirely through a Telegram conversation, with an AI team that never sleeps, never needs a meeting, and never asks for a status update.

No office. No standups. No Jira tickets. Just a phone and the right stack.

---

## The Stack

```
Raja (CEO / Architect)
    │
    │  Telegram (mobile — the only interface Raja needs)
    │
    ▼
Hermes (AI Team Lead)
    │
    ├── BMAD Agents    — specialist domain experts
    ├── gstack         — engineering workflow slash commands
    ├── Claude Code    — the execution engine (MCP + terminal + file)
    └── AURUM MCP      — the project's own pipeline, callable as a tool
```

---

## Layer 1 — Hermes: The AI Team Lead

**What it is:** [Hermes](https://github.com/garrytan/hermes) is a persistent AI agent runtime — think of it as a team lead that lives in your infrastructure 24/7. It has memory across sessions, can schedule tasks (cron), send messages to platforms, and invoke any tool in its toolset.

**What it does for AURUM:**
- Receives Raja's instructions via Telegram — on the bus, at 6am, wherever
- Maintains persistent memory of project state, decisions, team roster, and conventions
- Routes tasks to the right specialist (BMAD agent) or executes directly
- Can schedule autonomous runs — nightly DQ checks, CI failure alerts, morning briefings
- Delivers results back to Telegram — files, summaries, code, commit confirmations

**The key capability:** Hermes turns a conversation into a development environment. Raja doesn't open a laptop. He opens Telegram.

---

## Layer 2 — BMAD: The Specialist Team

**What it is:** [BMAD](https://github.com/bmad-ai/bmad-method) (Build Multi-Agent Development) is a framework for structured AI agent roles. Each agent has a name, a domain, a personality, and a specific responsibility in the development lifecycle.

**The AURUM team roster:**

| Agent | Role | Responsibility in AURUM |
|-------|------|------------------------|
| **Shazia** | Data Quality Lead | DQ rule design, profiling standards, anomaly threshold calibration |
| **Inaayah** | Technical Writer | Documentation, narrative docs, user-facing content |
| **Sofia** | Project Manager | Programme governance, milestone tracking |
| **Pierre** | Enterprise Architect | Location hierarchy, org design, cross-domain data model |
| **Gaurav** | Technical Architect | Pipeline architecture, MCP integration, performance |
| **Arun** | BI & Analytics Head | Golden record consumption, CLV models, reporting |
| **Nadia** | Data Governance Lead | Policy, stewardship workflows, regulatory alignment |
| **Tariq** | Security & Compliance | Sanctions screening, LEI validation, AML/CFT |
| **Jin** | Data Stewardship Lead | Daily stewardship queue, exception review |
| **Lena** | Data Integration Lead | Source system connectors, cross-domain reanchoring |
| **Carlos** | DataOps Engineer | Pipeline scheduling, monitoring, reverse sync |
| **Amara** | Business Analyst | Use case translation, stakeholder requirements |
| **Alishba** | UX Lead | Stewardship interface design, exception workflow UX |
| **Busi** | Data Migration Lead | Legacy system migration, CHARON pattern |

**How it works:** When Raja says "Inaayah, draft the LinkedIn post in my voice", Hermes routes to the tech writer agent with the right context — AURUM's narrative docs, Raja's writing conventions from memory, the target audience. The output arrives in Telegram ready to review.

**Configuration:** `~/Projects/BMAD/_bmad/custom/config.toml` — the custom config overrides the installer-managed defaults. Team names, descriptions, and specialisations are all configurable without touching installer files.

---

## Layer 3 — gstack: The Engineering Workflow

**What it is:** [gstack](https://github.com/garrytan/gstack) (90k+ GitHub stars) is a collection of SKILL.md files that give AI agents structured roles for software engineering workflows. 23+ slash commands, each a specialist persona.

**Installed at:** `~/.claude/skills/gstack/`
**Wired to AURUM via:** `~/Projects/AURUM/CLAUDE.md`

**The commands AURUM uses most:**

| Command | When Used |
|---------|-----------|
| `/office-hours` | Start of any new feature — reframes the idea before any code is written |
| `/plan-eng-review` | Architecture validation before implementation |
| `/autoplan` | Generate a bite-sized implementation plan from a spec |
| `/review` | Pre-commit code review — finds bugs that pass CI |
| `/ship` | Run tests → review → push → PR in one command |
| `/qa` | Full QA pass with real browser interaction |
| `/cso` | OWASP + STRIDE security audit |
| `/investigate` | Root cause deep dive when something breaks |
| `/retro` | Post-release retrospective |
| `/document-release` | Update all docs to match what just shipped |
| `/freeze` | Lock stable code from accidental AI edits |
| `/guard` | Activate careful + freeze together |

**The workflow in practice:**
```
Raja (Telegram): "Let's add vendor domain DQ rules"

Hermes → /office-hours   : Is this the right thing to build?
Hermes → /plan-eng-review: Architecture review
Hermes → /autoplan       : Implementation plan generated
Hermes → implements      : Code written, tests pass
Hermes → /review         : Pre-commit review
Hermes → /ship           : Committed, pushed, PR opened
Hermes → /document-release: CHANGELOG, README, docs updated
Raja (Telegram)          : "Done — here's the PR link"
```

---

## Layer 4 — Claude Code: The Execution Engine

**What it is:** [Claude Code](https://claude.ai/code) (Anthropic's CLI) is the agent that actually executes — writes files, runs terminals, calls MCP tools, reads codebases, patches files, manages git. It's the hands of the operation.

**How it connects:** Hermes invokes Claude Code as a subagent for any task that requires file system access, terminal execution, or code generation. Claude Code operates in the AURUM project directory with full access to the codebase.

**MCP tools available to Claude Code in this project:**
- `assay_schema` — inspect any CSV source file
- `unearth_profile` — profile any domain dataset for DQ issues
- `refine_match` — find duplicate candidates in any dataset

This means Claude Code can call AURUM's own pipeline as a tool while building AURUM. The refinery can inspect itself.

---

## Layer 5 — Telegram: The Only Interface

**What it is:** Telegram serves as the sole user interface for the entire development operation. Raja's phone is his development console.

**What happens over Telegram:**
- Feature requests → immediately routed to the right agent
- Code reviews → delivered as formatted messages
- CI failures → pushed as alerts (configured via Hermes cron)
- File deliverables → sent as native Telegram files
- Release confirmations → summary delivered when `git push` completes
- Morning briefings → scheduled stewardship summary (planned)

**The bot:** `MDM_Aurum_bot` — running as a launchd background service on the AURUM development machine. Always on. Always listening.

---

## The Development Day

What does a day of AURUM development actually look like?

**6:30 AM — Raja's phone**
> "Morning. Let's add the global compliance doc and sort the GitHub failures."

**Hermes:**
- Pulls last session context from memory
- Checks GitHub CI status → finds failures
- Reports: "3 failures, root cause is the demo hardcoded 50 rows. Fix is a 2-line change. Also need the compliance doc. Want me to do both?"

**Raja:** "Yes, go."

**Hermes:**
- Delegates CI fix to Claude Code → patches `demo/end_to_end_demo.py` → runs locally → confirms pass
- Delegates compliance doc to Nadia + Inaayah agents → 400-line doc written with all public framework links
- Commits both → pushes → CI goes green
- Cuts v0.2.0 release → creates GitHub release → delivers confirmation to Telegram

**Raja:** "Great. Now the blog post."

**Hermes → Inaayah:** Drafts the LinkedIn post in Raja's voice, pulling from the narrative docs already in the repo. Delivers to Telegram for review.

**Total elapsed time:** Under 2 hours.
**Meetings held:** 0.
**Lines of code Raja wrote personally:** 0.
**Quality of output:** Production-grade, committed, released, documented.

---

## Why This Stack, Not Another

**Why Hermes over a custom script?**
Persistent memory, multi-platform delivery, cron scheduling, and MCP toolset integration out of the box. Building this from scratch would take months.

**Why BMAD over prompt engineering?**
Named agents with defined roles create consistent, domain-appropriate outputs. "Inaayah, write this" produces different output than "write this" — the persona carries conventions, voice, and scope that survive across sessions.

**Why gstack over custom skills?**
90k stars means the workflow patterns are battle-tested. The slash command model maps naturally to how a software team actually operates. And it's already installed — zero setup cost.

**Why Telegram over a web UI?**
Always available, always authenticated, native file delivery, voice notes, no browser tab to manage. The best development interface is the one already in your pocket.

**Why Claude Code over a raw LLM API?**
File system access, terminal execution, git integration, MCP tool calling — all without writing infrastructure code. The agent does the mechanical work; the human does the directing.

---

## The Bigger Point

This stack is not about removing humans from software development. It is about removing **friction** from the parts of software development that don't require human judgment — the mechanical, the repetitive, the administrative.

Raja makes architectural decisions. Raja defines the vision. Raja reviews outputs and decides what ships. Raja is the one accountable for everything in the repository.

The stack handles execution. The human handles direction.

This is what software development looks like when the tools are right.

---

## Reproducing This Setup

Everything in this stack is open source or publicly available:

| Tool | Link | Cost |
|------|------|------|
| **Hermes** | [github.com/garrytan/hermes](https://github.com/garrytan/hermes) | Free |
| **BMAD** | [github.com/bmad-ai/bmad-method](https://github.com/bmad-ai/bmad-method) | Free |
| **gstack** | [github.com/garrytan/gstack](https://github.com/garrytan/gstack) | Free |
| **Claude Code** | [claude.ai/code](https://claude.ai/code) | Anthropic API pricing |
| **Telegram** | [telegram.org](https://telegram.org) | Free |
| **AURUM** | [github.com/RajaMDM/AURUM](https://github.com/RajaMDM/AURUM) | Free / MIT |

The only cost is Claude API usage — and for a project at this scale, it's a fraction of what a single contractor day would cost.

---

*Built by Raja Shahnawaz Soni. Executed by Hermes, BMAD, gstack, and Claude Code. Delivered via Telegram.*
