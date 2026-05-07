# AURUM FAQ — Common Questions, Plain Answers

> Drafted by the AURUM team using their specialist expertise.
> No jargon. No filler. Just answers.

---

## 🗄️ Storage & Data

### "Where does gbrain store the knowledge graph?"

**Short answer: On your machine. In one file. Nothing leaves your premises.**

```
~/.gbrain/brain.pglite
```

That's it — one file in a hidden folder on your laptop or server. No cloud account. No external server. No data leaving your network.

Inside that file, gbrain stores three layers:

| Layer | What it holds | Plain English |
|-------|--------------|---------------|
| **Pages** | MDM decisions, DQ rules, entity notes | The notebook |
| **Vectors** | Semantic embeddings for search | The intelligent index |
| **Graph links** | How entities connect | The web of relationships |

**The one-liner:**
> *"It's like a super-smart local database. Everything stays on your machine. When the team needs shared access across machines, one command migrates it to a hosted database."*

---

### "What if we need multiple people to access it?"

That's when you move from **PGLite** (local file) to **Postgres via Supabase** (hosted). One command:

```bash
gbrain migrate --to supabase
```

Everything migrates — pages, embeddings, graph links, timeline, decisions. Zero data loss. Then anyone on the team can query the same brain from any machine.

**Options by team size:**

| Setup | Best for | Cost |
|-------|---------|------|
| PGLite (default) | Solo, learning, evaluation | Free |
| Supabase cloud | Small-medium teams, fast setup | ~$25/month |
| Self-hosted Postgres | Enterprise, data residency requirements | Your infra cost |

---

## 🏢 Enterprise Deployment

### "If someone wants to deploy AURUM officially at their organisation, what are their options?"

*Answered by **Pierre** (Enterprise Architect) and **Tariq** (Security)*

---

AURUM runs in three runtimes — CLI, HTTP API, and MCP server. All three can be deployed on-premise. Here are your paths:

---

#### Option 1 — Laptop / Developer Machine (Evaluation)

**Best for:** Individual practitioners, proof of concept, learning the codebase.

```
Your Laptop
├── AURUM pipeline (Python, runs locally)
├── gbrain (PGLite, one file at ~/.gbrain/brain.pglite)
└── Hermes AI agent (optional, local)
```

**Data stays:** Entirely on your machine.
**infosec approval needed:** Minimal — no network exposure.
**Setup time:** 30 minutes.

---

#### Option 2 — On-Premise Server (Team Deployment)

**Best for:** Teams that need shared access, stricter data residency, or internal audit requirements.

```
Your Internal Server (Linux/VM/Kubernetes)
├── AURUM pipeline (Python, containerised via Docker)
├── Postgres + pgvector (self-hosted, your DBA manages it)
├── gbrain (PostgresEngine, points to your internal Postgres)
└── Hermes AI agent (optional, internal endpoint)
```

**Data stays:** Entirely within your network perimeter.
**AI calls go to:** Whichever provider your infosec team has approved — Azure OpenAI (data residency guarantees), on-premise Ollama, or any OpenAI-compatible API.
**infosec approval needed:** Standard server + database approval. No public endpoints required.
**Setup time:** 1–2 days.

Key decisions your team will make:

| Decision | Options |
|----------|---------|
| Where does Postgres run? | Existing internal DB, new VM, Kubernetes pod |
| Which AI provider? | Azure OpenAI (recommended for regulated orgs), AWS Bedrock, on-prem Ollama |
| Who manages the server? | Your DevOps / CloudOps team |
| How do stewards access it? | Internal web UI, CLI, or via MCP-compatible tools (Cursor, Claude Code) |

---

#### Option 3 — Cloud Deployment (Managed, Air-Gapped Optional)

**Best for:** Organisations that prefer managed infrastructure but still need data sovereignty.

```
Cloud (Azure / AWS / GCP — your approved provider)
├── AURUM pipeline (container, auto-scaled)
├── Postgres on managed cloud DB (Azure Database, RDS, CloudSQL)
├── gbrain (PostgresEngine → managed Postgres)
├── Supabase (optional managed Postgres alternative)
└── AI endpoints → Azure OpenAI / Bedrock (data stays in your region)
```

**Data stays:** In your cloud tenancy, in your chosen region.
**Data residency:** Configurable — UAE North, UK South, EU West, etc.
**Compliance:** GDPR, UAE PDPL, KSA PDPL, and other jurisdictional requirements met by choosing the right region + provider.
**Setup time:** 2–5 days with your DevOps team.

---

#### Option 4 — Air-Gapped / No External AI Calls

**Best for:** Banks, government entities, defence contractors — any org where data cannot leave the building and internet access is restricted.

```
Air-Gapped Internal Network
├── AURUM pipeline (Python, offline)
├── Postgres + pgvector (internal)
├── gbrain (PostgresEngine, internal Postgres)
└── AI layer → Ollama running local models (Llama 3, Mistral, etc.)
              → No internet required. No API keys leaving.
```

**Data stays:** 100% on-premise. Zero external calls.
**AI model:** Runs locally on your GPU servers via Ollama or llama.cpp.
**Trade-off:** Local models are less capable than GPT-4/Claude for complex reasoning. Quality of AI-generated DQ rules and match suggestions will be lower — but still useful for routine automation.
**Setup time:** 1–2 weeks (model selection, GPU provisioning, tuning).

---

### "What about the AI calls — do our data go to OpenAI?"

**Only if you choose OpenAI.** The AI layer is pluggable.

| AI Provider | Data leaves your network? | Best for |
|-------------|--------------------------|---------|
| **OpenAI** | Yes → OpenAI's servers | Developer/personal use |
| **Azure OpenAI** | No → stays in your Azure tenant | Regulated enterprises |
| **AWS Bedrock** | No → stays in your AWS account | AWS-first orgs |
| **Ollama (local)** | No → runs on your own GPU | Air-gapped / max privacy |
| **llama.cpp** | No → runs on your CPU/GPU | Fully offline |

The pattern is the same regardless of provider. The pipeline doesn't care which AI you use — swap the endpoint and the key. *Use whatever your infosec team has approved.*

---

### "Does AURUM need an internet connection to run?"

**No.** The pipeline itself is pure Python — no internet required.

What *might* need internet, depending on your setup:

| Component | Internet needed? | Alternative |
|-----------|-----------------|-------------|
| AURUM pipeline | ❌ No | Runs offline |
| gbrain (PGLite) | ❌ No | Local file |
| gbrain (Supabase) | ✅ Yes | Self-hosted Postgres |
| OpenAI embeddings | ✅ Yes | Ollama embeddings locally |
| Anthropic API | ✅ Yes | Local model |
| GitHub (code updates) | ✅ Yes | Air-gap: clone once, update manually |

Full offline operation = PGLite + Ollama + no external integrations. Fully supported.

---

### "Who manages access control?"

AURUM doesn't ship with a built-in auth layer — by design. It plugs into *your* existing IAM:

- **On-premise:** Your AD / LDAP / internal SSO
- **Cloud:** Azure AD, AWS IAM, GCP IAM
- **Database level:** Postgres row-level security (RLS) — gbrain supports this on the Postgres engine
- **API layer:** Your API gateway (Kong, NGINX, Azure APIM)

This is intentional — AURUM is a reference implementation. Your enterprise security team owns the access control layer.

---

### "Can we run AURUM on Kubernetes?"

Yes. The pipeline is containerised. A basic Helm chart or Kubernetes manifests would cover:

- AURUM pipeline deployment
- Postgres + pgvector StatefulSet (or point to your existing managed DB)
- gbrain sidecar or separate deployment

This is on the AURUM roadmap. Community PRs welcome.

---

## 📋 Compliance & Audit

### "How does AURUM help with data compliance?"

Every action in AURUM is logged in the MARK stage — immutable, timestamped, attributed. This covers:

- **Subject Access Requests (GDPR / UAE PDPL):** Query all data for a person in seconds
- **Right to Erasure:** Cascade delete from all linked source records
- **Audit trail:** Every ingestion, DQ flag, merge decision, steward approval — all traceable
- **Lineage:** Who touched what, when, and why

Full detail → [`docs/DATA_SOVEREIGNTY_AND_COMPLIANCE.md`](DATA_SOVEREIGNTY_AND_COMPLIANCE.md)

---

### "Is AURUM production-ready?"

**AURUM is a reference implementation, not a product.**

That means:
- ✅ The architecture is production-grade — patterns, lineage, stewardship, compliance
- ✅ The use-case library covers 41 real-world MDM scenarios
- ✅ The code is working, tested, CI green
- ❌ It does not ship with enterprise support, SLAs, or a managed service

Think of it as the **blueprint** — your engineering team builds from it, adapts it, and runs it on your infrastructure. The patterns transfer. The implementation is yours to own.

---

## 🧠 gbrain — Knowledge Graph

### "What exactly does gbrain add that AURUM doesn't already have?"

AURUM records *what happened* — the lineage log.
gbrain records *why it happened* — the reasoning, the context, the institutional knowledge.

| Question | AURUM answers | gbrain answers |
|----------|--------------|----------------|
| Was this record merged? | ✅ Yes — MARK stage logs it | ✅ Yes — and here's why |
| Which records were merged? | ✅ Full cluster in golden record | ✅ Full context + related decisions |
| Who approved it? | ✅ Steward ID in log | ✅ And what they considered |
| Why was this DQ rule written? | ❌ Not stored | ✅ Full rationale, linked to incident |
| What did we decide last time this pattern appeared? | ❌ Not searchable | ✅ Semantic search finds it instantly |
| What does a new steward need to know? | ❌ Manual briefing | ✅ One query, full context |

---

### "What is the nightly dream cycle?"

Every night at 2 AM, an automated job runs against the knowledge graph. It:

1. **Scans** today's sessions for MDM entities mentioned
2. **Creates or enriches** brain pages for each entity
3. **Syncs** any new AURUM docs into the vector index
4. **Consolidates** recurring patterns into permanent knowledge

The result: the brain gets smarter every night without any manual effort. Knowledge that appeared in three separate sessions this week becomes a permanent brain page by the weekend.

---

*AURUM v0.2.0 · github.com/RajaMDM/AURUM*
*Team: Pierre (EA), Tariq (Security), Gaurav (Tech), Shazia (DQ), Nadia (Governance), Jin (Stewardship)*
