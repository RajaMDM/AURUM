# Phase 4 — Anti-match rule audit (2026-05-03)

Per-record forensic audit done before deciding where to implement the anti-match rule ("when names match but phones differ, route to STEWARD_REVIEW regardless of composite score"). Conclusion drives the Phase 4 spec's "Out of scope today" section in `phase4_flow_specifications.md`.

## Question 1 — Does the rule fire on any current high-confidence demo record?

**Answer: NO. 0 of 6 high-confidence demo records would shift from SURVIVED to STEWARD_REVIEW under the new rule.**

All phone values extracted from `scripts/load_sample_data.py` (line numbers cited):

| Demo record | Composite | Canonical phone (primary) | Staging phone (raw) | Phone match? | Source line |
|---|---:|---|---|:---:|:---:|
| Priya ECOMM | 0.89 | `+971-50-555-1042` | `+971-50-555-1042` | ✓ | canonical:704, staging:760 |
| Priya LOYALTY | 1.00 | `+971-50-555-1042` | `+971-50-555-1042` | ✓ | canonical:704, staging:785 |
| Sarah CRM | 1.00 | `+971-50-318-9921` | `+971-50-318-9921` | ✓ | canonical:923, staging:952 |
| Sarah ECOMM | 0.85 (boost-floor) | `+971-50-318-9921` | `+971-50-318-9921` | ✓ | canonical:923, staging:975 |
| Aisha CRM | 1.00 | `+971-55-227-3309` | `+971-55-227-3309` | ✓ | canonical:1034, staging:1067 |
| Aisha LOYALTY | 1.00 | `+971-55-227-3309` | `+971-55-227-3309` | ✓ | canonical:1034, staging:1091 |

**Sarah Chen demo (Flow 1 hero record): NOT BROKEN.** Both Sarah CRM (composite=1.00) and Sarah ECOMM (composite=0.85, name_boost_floor active) have phones identical to canonical. Auto-approve survives.

**Aisha Mubarak linked-tuple demo: NOT BROKEN.** Both Aisha CRM and LOYALTY have phones identical to canonical.

**Priya Krishnamurthy hero demo: NOT BROKEN.** All 3 staging-to-canonical phones identical.

### Why all phones happen to align

Structural reason — AURUM matcher uses phone as a positive scoring signal (`phone_score × 0.10` in weighted total). When phones don't match, composite drops by up to 0.10. To still cross 0.85, name_boost_floor must activate (name_score ≥ 0.90 with email also imperfect). Sarah ECOMM is the closest case to this — boost-floor active, but her phone IS still identical between B2B and consumer contexts.

### Borderline-band record (FYI, not in Flow 1's filter range)

| Mohammed CRM | 0.60 | `+971-50-444-7821` | `+971-50-444-7821` | ✓ | canonical:844, staging:873 |

Phone match here is what kept Mohammed at 0.60 instead of dropping below the candidate filter. Anti-match rule would not fire (composite below 0.85 anyway).

### Demo coverage gap

Building flow infrastructure for a rule that fires on zero current demo records = building un-exercised code. To exercise the rule we'd need a new demo record. Concrete suggestion (deferred to Phase 5): "Sarah Chen Dubai" — same name as canonical Sarah, same email, but different phone (e.g., last 4 digits swapped). Should land at composite ≥ 0.85 via name_boost_floor (name=1.0, email=1.0, phone=0 → weighted=0.90, floor=0.85), then anti-match flag flips processing_status to STEWARD_REVIEW.

---

## Question 2 — Is phone normalization reliable for flow-level comparison?

**Answer: format is uniform on all "good" data, but matcher's normalization should remain the source of truth.**

### Storage format observed

All hand-coded demo records + the `random_uae_phone()` filler generator produce the same shape:

```
+971-{prefix}-{NNN}-{NNNN}
```

where prefix ∈ `{50, 52, 54, 55, 56, 58}` (UAE_MOBILE_PREFIXES, `load_sample_data.py:328`).

### Malformed inputs (controlled, intentional)

`random_uae_phone(malformed_chance=...)` (`:533`) introduces these abnormal forms with 8–10% probability on filler stagings only:

- `"050123"` (truncated)
- `"+971-50-XXX"` (literal X placeholder)
- `"0501234567890"` (overlong)
- `"TBD"` (literal)

Never appear in canonical records or in the 5 hand-coded demo-story builders.

### Source-of-truth normalization (public AURUM matcher)

From `~/Projects/AURUM/refine/matching/matcher.py:77-79`:

```python
phone_a = "".join(c for c in rec_a.get("phone","") if c.isdigit())[-9:]
phone_b = "".join(c for c in rec_b.get("phone","") if c.isdigit())[-9:]
phone_score = 1.0 if phone_a and phone_a == phone_b else 0.0
```

= "strip non-digits, take last 9 digits, equality compare." This is what `phone_score` uses.

### Power Fx equivalent (if Option A had been chosen)

```
Right(Substitute(Substitute(Substitute(Substitute(Substitute(phone, "-", ""), "+", ""), " ", ""), "(", ""), ")", ""), 9)
```

Verbose, brittle, and creates a second source of truth (matcher's normalization vs flow's normalization). OData filter expressions cannot do regex-like normalization, so the comparison would have to live in a post-trigger Condition step against a Get-a-Row of the canonical (extra Dataverse API call per Flow 1 run).

---

## Recommendation: Option B (defer to AURUM v0.3.0)

Reasoning condensed (full version in `phase4_flow_specifications.md` "Out of scope today" section):

1. **Zero current demo coverage** — would build un-exercised infrastructure
2. **Architectural fit** — anti-match is matching logic, belongs in matcher, not workflow
3. **Single source of truth for phone normalization** — matcher already has it
4. **Flow mechanics cost** — adds Get-a-Row + Condition step per Flow 1 run for zero current benefit
5. **Demo-narrative honesty** — "AURUM v0.3.0 implements it cleanly" beats "we bolted it on at workflow layer"

ROADMAP.md updated with Phase 5 scope: AURUM matcher emits `discriminator_conflict: bool` flag → AURUM-PP regenerates sample data with Sarah Chen Dubai exemplar → existing Flow 2 picks up the resulting STEWARD_REVIEW state.
