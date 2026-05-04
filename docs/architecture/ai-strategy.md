# AI / ML Strategy in AURUM

> Where LLMs and classical ML each earn their keep across the MDM lifecycle —
> and where they don't.

This document records *why* AURUM uses what it uses, so future contributors
don't add LLM calls reflexively when a regex would do, or hand-build heuristics
when a model would obviously do better. It also pre-empts the inevitable
review-board question: *"shouldn't this be using AI?"*

---

## The premise

MDM has four hard problems and they don't all have the same solution.

| Problem | What it really is | Right tool |
|---|---|---|
| **Format dirt** | "Phone number written 47 different ways" | Regex / standardization rules |
| **Match decision** | "Is `John Smith @ +971-50…` the same person as `J. Smyth @ 971501234567`?" | Classical fuzzy + edit-distance, deterministic |
| **Anomaly** | "This row's combination of values is unlike any other row" | Statistical / ML (Isolation Forest, density estimation) |
| **Rule authoring** | "*Phone numbers must be UAE-format if country is UAE*" → executable code | LLM with structured output, **human-reviewed** |

LLMs are extraordinary at the last problem and mediocre-to-bad at the first
three. Classical methods are extraordinary at the first three and useless at
the fourth. AURUM treats this as a routing decision, not a religion.

---

## Where LLMs are the right tool

### 1. Rule authoring (UNEARTH `llm_rules/`, v0.2.0)
A business steward can describe a rule in prose: *"loyalty members from
the UAE without an Emirates ID need a passport scan on file."* Translating
that into executable validation code is the work LLMs are best at — they
take ambiguous English and emit structured Python.

The output is **never trusted blind**. The generated rule is committed
into `unearth/rules/generated/` with the prompt that produced it, reviewed
by a human, and only then promoted into the active rule set. Versioning
is mandatory. Audit beats novelty.

### 2. Borderline match adjudication (REFINE LLM tiebreaker, v0.2.0)
The matcher emits a composite score in `[0, 1]`. Above 0.65 → match.
Below 0.55 → not a match. Between those is the *agonising middle*: pairs
where the deterministic features are inconclusive and a human steward
would normally be queued.

For pairs in `[0.55, 0.65]`, AURUM invokes an LLM with the two records
and asks a single structured question: *"Are these the same entity?
Return `match | non-match | unclear` with one-sentence justification."*
The LLM either resolves the pair or escalates to a steward queue. Cost
is bounded because the borderline zone is, by construction, a small
fraction of pairs.

### 3. Anomaly explanation (UNEARTH steward UI, v0.2.0)
The Isolation Forest flags a row as anomalous. It cannot tell you *why*
in business terms. An LLM, given the row and the reference distribution,
produces a one-sentence steward-readable reason ("phone country code
disagrees with billing country") that turns a numeric outlier into a
ticket someone can act on.

### 4. Steward summaries (UNFURL, MARK, v0.3.0+)
Lineage events, golden record changes, downstream sync impact — all
produce structured logs that humans need to read in prose. LLMs handle
this well and the output is informational, not decisional, so
hallucinations cost a steward five seconds, not a corrupted master.

---

## Where LLMs are the wrong tool

### Matching at scale
A real customer master has 10⁵ to 10⁸ records. Pairwise comparison is
the inner loop. An LLM call per pair is impossible economically and
unjustifiable epistemically — you cannot reproduce the same answer twice
under temperature > 0, and at temperature 0 you've paid the inference
cost to get a deterministic answer that RapidFuzz returns in microseconds.

REFINE uses **RapidFuzz token scoring + Jellyfish Jaro-Winkler + a
composite weighting (name 0.65 / email 0.25 / phone 0.10) with a
name-boost floor**. This is deterministic, auditable, fast, and survives
re-running on the same data forever. No LLM in the matcher.

### Survivorship
"Pick the cleanest version of each attribute" is a deterministic
problem with documented rules: longer non-default values, more recent
update timestamps, source-system trust ranks. Survivorship answers must
reproduce identically across every run — an auditor will ask why the
golden record changed and the answer cannot be *"the model felt
different about it today."*

### Identity resolution thresholds
The 0.65 threshold isn't a model-tunable parameter — it's a calibrated
operating point chosen against labelled match pairs. Sliding it via
LLM "judgement" makes the system non-stationary in a way no auditor
will accept.

### Anomaly detection
Outliers are a statistical problem. **Isolation Forest** wins because
it has a closed-form complexity, runs in seconds on millions of rows,
and produces a stable score that can be thresholded. LLMs can't do
this — they have no notion of "the rest of the dataset" without
prompt-stuffing it, which scales to nowhere.

---

## The risk frame

Every place AURUM uses an LLM, the architecture answers four questions:

1. **What happens if it hallucinates?**
   Rule generator: human reviews before promotion.
   Tiebreaker: bounded blast radius (only borderline pairs); steward
   queue is the fallback path, not the LLM's answer.
   Anomaly explanation: steward sees the original row beside the
   explanation; wrong reason is annoying, not catastrophic.

2. **Can we replay the answer?**
   Every LLM call logs `(model, version, prompt_hash, output, timestamp)`.
   For the rule generator and tiebreaker, the output is committed.

3. **What does it cost per 1M records?**
   Matching at every pair: estimate ≥ $50,000 per million records on
   current frontier-model pricing. Tiebreaker on borderline only:
   estimate < $50 per million records (since < 0.1% of pairs hit the
   borderline zone). The economics dictate the architecture.

4. **What's the steward escalation path?**
   Every LLM-touched decision has an "I'm not sure" outcome that
   routes to a human queue. The system is permitted to give up; it is
   not permitted to confabulate.

---

## Provider neutrality

The Anthropic API is the v0.2.0 reference backend (it's what the maintainer
uses daily). The interface in `unearth/llm_rules/` is provider-agnostic:
the same prompts work against OpenAI, Azure OpenAI, Bedrock-hosted Claude,
or a local model behind an OpenAI-compatible endpoint. Switching providers
is a config-file change, not a code change. This matters because most
enterprises will land on whichever provider their procurement team
already approved, not whichever has the best model this month.

---

## What's *not* in AURUM and why

- **No LLM "agentic" pipeline orchestration.** The pipeline is five
  stages running in order. Adding agentic loops adds non-determinism
  to a system whose value proposition is reproducibility.
- **No vector embeddings for matching.** Embedding similarity collapses
  the very signals (token order, edit distance, phonetic equivalence)
  that classical matchers exploit. They underperform RapidFuzz on
  short structured strings like names and SKUs.
- **No fine-tuned models.** The rule generator and tiebreaker run on
  zero-shot frontier models with structured-output schemas. Fine-tuning
  is on the table only if a measured failure mode demands it.
- **No "AI steward" replacement.** Stewards review rule promotions,
  borderline pairs that the LLM marked unclear, and Isolation Forest
  outliers. AURUM augments the steward queue; it doesn't aim to empty it.

---

## Summary

| Stage | Classical | LLM | Status |
|---|---|---|---|
| ASSAY | Schema inspection, type inference | — | ✅ v0.1.1 |
| UNEARTH | All 7 domain profilers, regex/whitelist rules | Rule generator from prose | ✅ profilers v0.1.2 · 📋 LLM rules v0.2.0 |
| UNEARTH | Isolation Forest anomaly detection | Anomaly explanation | 📋 v0.2.0 |
| REFINE | RapidFuzz + Jaro-Winkler matcher, deterministic survivorship | Borderline-pair tiebreaker | ✅ matcher/survivorship v0.1.1 · 📋 tiebreaker v0.2.0 |
| UNFURL | Publisher registry | Steward-readable change summaries | 🔧 publisher stub · 📋 LLM v0.3.0 |
| MARK | Deterministic lineage tracking | Lineage prose summaries | ✅ tracker v0.1.1 · 📋 LLM v0.3.0 |

The defensible position: **classical methods do the work; LLMs do the
last mile that classical methods can't reach.** The line between them
is drawn by economics and audit, not by enthusiasm.

---

*Document maintained by [Raja Shahnawaz Soni](https://linkedin.com/in/raja-shahnawaz/).
Disagreements welcome via [Discussion](../../discussions) — this is an
opinionated stance, not a settled science.*
