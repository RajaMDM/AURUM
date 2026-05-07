# LinkedIn Article — Long Form
# "I Rebuilt My MDM Practice From Scratch Using AI. Here's What I Learned."
# Raja Shahnawaz Soni
# Target: 2,000–2,500 words | LinkedIn Article (not a post)
# Tone: Practitioner voice. Honest. No hype. Story-driven.
# Status: Ready for Raja's review

---

**I Rebuilt My MDM Practice From Scratch Using AI. Here's What I Learned.**

---

Twenty years ago, I walked into my first Master Data Management project. We were using a vendor platform that cost more per year than some of my clients' entire IT budgets. We had a team of twelve. We had a governance committee. We had a steering group. We had a project plan that was already six months old before the first data was touched.

Eighteen months later, we had a golden record for the customer domain.

One domain. Eighteen months. Twelve people.

I've spent two decades watching this story repeat across industries and geographies. The scale changes. The vendor names change. The PowerPoints get slicker. But the shape of the problem — and the shape of the solution — barely moves.

This year, I decided to rebuild the whole thing from scratch. By myself. In my spare time. Using AI.

What I built is called AURUM. It's open source, MIT licensed, and live on GitHub. But this article isn't really about AURUM. It's about what I learned doing it — about MDM, about AI, about the gap between how we've always done this and how it could be done.

---

**First — why MDM is still broken in 2025**

Let me be direct: the reason MDM programmes fail isn't the technology. It's the human attention cost.

Every traditional MDM programme runs on the same fuel: skilled humans doing careful, repetitive work. Data engineers write ingestion rules by hand. DQ analysts maintain hundreds of quality checks in spreadsheets. Data stewards process exception queues that never empty. Matching algorithms run on fixed thresholds that nobody remembers who set or why.

At small scale, this is manageable. At enterprise scale, it becomes a bottleneck that no amount of vendor licensing can solve. The backlog of DQ rules that never got written. The stewardship queue that the team has quietly stopped reviewing. The matching threshold that was set to 0.75 in 2018 and has never been touched because nobody wants to own what happens if they change it.

The discipline is sound. The approach is not.

MDM doesn't need better software. It needs a different relationship between human attention and mechanical work. And in 2025, for the first time, we actually have the tools to redesign that relationship.

---

**What AI actually changes — and what it doesn't**

I want to be careful here, because this is where most AI conversations go wrong.

AI does not replace the data practitioner. It does not replace the steward's judgment. It does not replace the governance decision about which system is authoritative for a given field. These are human responsibilities, and they will remain human responsibilities for a very long time.

What AI changes is the *supply* of mechanical work. And in MDM, mechanical work is everywhere.

Consider data quality rules. The traditional process: a steward describes what she knows about the data, a DQ analyst interprets it, an engineer writes the code, it goes through a release cycle, it arrives in production three to four weeks later. By then, the data has changed and the rule is already partially wrong.

The new process: the steward describes what she knows, in plain English. An AI generates deterministic, inspectable, auditable code — not a black box model, but actual Python that she can read and verify. A human reviews it. If it's right, it goes straight to the review queue. If it's wrong, she corrects the description and it regenerates.

The four-week cycle becomes a four-second generation plus a thirty-second review.

Now multiply that across hundreds of rules, seven domains, and multiple source systems. The bandwidth difference is not incremental. It is structural.

---

**The stewardship bottleneck**

The stewardship queue is where most MDM programmes quietly die.

In theory, data stewards review every flagged record, every borderline match, every DQ exception. In practice, at any serious scale, the queue grows faster than it can be processed. Teams learn to skim. They approve things they shouldn't. They miss things they should catch. Not because they're bad at their jobs — because they're human, and humans have a finite capacity for careful, repetitive decision-making.

I built AURUM around a three-tier decision model:

**Tier 1 — Resolve automatically.** Name casing. Country code normalisation. Phone format standardisation. Date format reconciliation. These are deterministic transformations. They don't benefit from human review. They just need to be logged and auditable. An AI doesn't add value here — but a rule does, and the rule can run at machine speed.

**Tier 2 — AI proposes, human approves.** Probable duplicate matches. Field conflicts with a clear winning source. Hierarchy proposals. Rehire detection. For these, the AI packages the decision: here are the two records, here is the match score, here is the basis, here is my proposal, here is the risk if I'm wrong. The steward reviews the package and approves or rejects. Thirty seconds. One click.

**Tier 3 — Human judgment required.** Different bank accounts on a probable duplicate vendor. A counterparty jurisdiction change. Corporate restructuring. Regulatory decisions. Anything where being wrong has legal, financial, or reputational consequences. These go to a specialist human. No AI proposal. Full context. Proper attention.

The result: a programme that previously needed eight full-time stewards handling four hundred decisions a day can run with three stewards handling sixty Tier 2 decisions and fifteen Tier 3 escalations — and make better decisions, because the humans are never fatigued by the trivial.

---

**Seven domains talking to each other**

Here's the thing about MDM that vendor demos never show you: the real value isn't in mastering one domain. It's in what happens when all your domains know about each other.

A customer golden record that doesn't know which products that customer bought is just a deduped contact list. A product golden record that doesn't know which vendors supply it is just a cleaned PIM export. An employee record that doesn't know which location that employee works at is just a tidy HRMS extract.

The power comes from the web. When the customer knows the product. When the asset knows the location and the employee. When the counterparty knows it's also the vendor and the customer. When a single business event — say, opening a new store — cascades correctly through all seven domains simultaneously: Location mastered first, then Employee and Asset provisioned to that location, then Product and Vendor qualified for that store, then the landlord onboarded as a Counterparty, and finally the Customers in the catchment area reassigned.

That cascade, done correctly, means the store opens on Day 1 with zero data blockers. Every system sees the right IDs. Every golden record links to every other golden record it should. The lineage trail is complete from the moment the location was created.

Done incorrectly — or done piecemeal, one domain at a time, with no cross-domain linkage — and you get what I've seen in nearly every enterprise MDM programme I've ever worked on: clean silos that don't talk to each other, cross-domain foreign keys that go stale the moment MDM runs, and a CFO who still can't get a single number for total exposure to a given counterparty because the counterparty appears as a customer in CRM, a vendor in ERP, and an FX counterparty in Treasury — three golden records, no link between them.

I documented all of this in AURUM's use-case library. Forty-one real-world MDM scenario playbooks, organised in three tiers: single-domain, cross-domain pairs, and one grand scenario where all seven domains cascade from a single business event. Not to sell anything. Because I've never seen it written down anywhere in a form that a practitioner can actually use.

---

**How I'm running this — and why the tools don't matter**

I want to talk about how I'm building AURUM, but I want to do it in a way that's honest about what's transferable and what isn't.

I use an AI agent runtime as my team lead. It runs on my own machine, connects to a messaging platform I already use on my phone, and has persistent memory across sessions. When I send it a message — from anywhere, at any time — it picks up where we left off, executes the task, and sends me back the result. Code committed. Release cut. CI checked. Document drafted. All confirmed back to me on my phone.

I have a set of specialist AI agents, each scoped to a domain: one for data quality, one for governance, one for compliance, one for architecture, one for documentation, and so on. When I need a governance decision made, I route to the governance agent. When I need documentation written in my voice, I route to the writer. The agents have names and personalities and specific areas of responsibility. They are not general-purpose chatbots — they are scoped specialists.

I have a library of engineering workflow patterns — structured prompts that map to real software team roles. Before I build anything, I run an architecture review. Before I commit anything, I run a code review. Before I ship anything, I run a QA pass. These aren't manual steps I remember to do — they're part of the workflow, invoked consistently, producing consistent outputs.

And then there's the execution layer — the AI that actually writes files, runs terminals, calls git, reads the codebase, patches code, and manages releases.

Now here's the honest part: **none of the specific tools I use are the point.**

The pattern is the point.

Any AI agent runtime with persistent memory and a messaging interface can play the team lead role. Any structured agent framework can play the specialist team role. Any workflow pattern library can play the engineering process role. Any capable coding AI can play the execution role. Any messaging platform your organisation already uses and approves can be the interface.

The specific tools I use are the ones that work for me, on my hardware, in my workflow, with my infosec constraints. They happen to be open source. But they could be entirely different tools for someone else — enterprise-grade, vendor-supported, security-reviewed, SOC 2 compliant — and the pattern would work exactly the same way.

What matters is not which tools you use. What matters is that you have:
- A persistent AI layer that remembers context across sessions
- Specialist agents scoped to specific domains and responsibilities
- Structured workflow patterns that enforce consistent engineering practices
- A human in the loop for every decision that matters
- An audit trail for everything the AI does

If your organisation's infosec team has approved a specific AI coding assistant, use that. If your enterprise has a sanctioned AI platform, use that. If you're in a regulated environment with strict data residency requirements, run everything on-premise. The pattern transfers. The specific implementation is yours to choose.

---

**What I've learned**

Twenty years of MDM taught me what the problems are. This year taught me that most of the constraints I'd accepted as fixed are actually just the cost of the old toolset.

The four-week DQ rule cycle is not inevitable — it's a consequence of the sequential handoff between steward, analyst, and engineer. Remove the handoff and the cycle collapses.

The stewardship bottleneck is not inevitable — it's a consequence of routing all decisions through the same human channel regardless of complexity. Route by tier and the bottleneck disappears.

The single-domain silo is not inevitable — it's a consequence of MDM programmes that never planned for cross-domain linkage. Build the cross-domain entity registry from day one and the silos become a web.

The eighteen-month golden record is not inevitable. It is a symptom of a programme designed around the constraints of 2005.

None of this means MDM is easy. The business rules are still hard. The survivorship decisions are still consequential. The regulatory compliance is still non-negotiable. The human judgment at the Tier 3 level is still irreplaceable.

But the mechanical work — the rules, the profiling, the matching candidates, the documentation, the routine stewardship decisions — that is now compressible in a way it has never been before.

The refinery can be intelligent. The question is whether you're willing to redesign it.

---

**AURUM**

Everything I've described is implemented in AURUM — a fully working, open-source, MIT-licensed MDM reference implementation.

Five pipeline stages. Seven domains. Three runtimes: CLI, HTTP API, and MCP server (so any AI agent can call the pipeline as a native tool). Forty-one use-case playbooks. A global data sovereignty guide covering GCC and worldwide frameworks with official document links. A narrative on what MDM looks like in the AI era. And a disclaimer: all company names are fictional, any resemblance coincidental.

It is not a commercial product. It is not a framework to adopt wholesale. It is a reference — a working example of what I believe MDM should look like, built the way I believe it should be built, documented the way I wish every MDM programme was documented.

If you find something useful in it, use it. If you disagree with something in it, I'd genuinely like to know why.

**github.com/RajaMDM/AURUM**

---

*I've spent twenty years in enterprise data — across financial services, retail, public sector, and technology. I build things rather than theorise about them. If you're working on MDM, data governance, or AI-augmented data management and want to compare notes — my DMs are open.*

---

**#MasterDataManagement #DataGovernance #DataQuality #AI #AgenticAI #OpenSource #DataEngineering #MDM #DigitalTransformation #EnterpriseData #BuildInPublic**

---
> Version: v3 — Long form article
> Word count: ~2,100
> Format: LinkedIn Article (not a post — use the "Write article" option, not "Start a post")
> Tip: Post the GitHub link as first comment, not in the article body — LinkedIn suppresses external links in article reach
> Images to consider: AURUM pipeline diagram from README, the 7-domain web diagram, the 3-tier stewardship model
