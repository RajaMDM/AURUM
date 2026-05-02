# REFINE — Stage 03

**Metallurgical meaning:** The furnace. Heat separates impurities from metal. Multiple ore samples go in — pure gold comes out. One thing, not many.

**MDM meaning:** REFINE is where the real MDM work happens. Blocking narrows the search space. Matching scores record pairs. Survivorship picks the best attribute from each source. Golden record assembly produces the one trusted record that every downstream system will navigate by.

## Responsibilities
- Blocking (sorted neighbourhood, LSH, rule-based)
- Fuzzy matching (RapidFuzz, Jaro-Winkler, token scoring, ML classifier)
- Survivorship rule execution (trust-weighted, most-complete, most-recent)
- Golden record assembly and trust scoring
- Match review queue for steward intervention

## Key Components
- `blocking/` — candidate pair generation
- `matching/` — composite scoring engine
- `survivorship/` — attribute-level survivorship rules
- `golden_record/` — assembly, trust scoring, golden flag

## Trust Score Formula
`trust_score = filled_key_fields / total_key_fields`
Key fields: first_name, last_name, email, phone, city, country

## When REFINE is Complete
- All candidate pairs scored
- Match/no-match decisions recorded
- Golden record produced with trust_score ≥ 0.6
- Steward exceptions routed to review queue
