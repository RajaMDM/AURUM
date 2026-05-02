"""
REFINE Matcher
Fuzzy matching engine using RapidFuzz + Jaro-Winkler + token scoring.
Produces match candidates with confidence scores for survivorship.

Composite scoring:
    name_score  * 0.65
  + email_score * 0.25
  + phone_score * 0.10
  → with a NAME-BOOST FLOOR of 0.85 * name_score when name match is very strong.

The boost recognises a real-world MDM truth: when two records have a
near-identical name, that alone is significant evidence of identity even
when contact details diverge across systems.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any
import pandas as pd

try:
    from rapidfuzz import fuzz
    RAPIDFUZZ_AVAILABLE = True
except ImportError:
    RAPIDFUZZ_AVAILABLE = False

try:
    import jellyfish
    JELLYFISH_AVAILABLE = True
except ImportError:
    JELLYFISH_AVAILABLE = False


MATCH_THRESHOLD: float = 0.65
NAME_BOOST_MULTIPLIER: float = 0.85


@dataclass
class MatchCandidate:
    record_a_id: str
    record_b_id: str
    composite_score: float
    name_score: float
    email_score: float
    phone_score: float
    is_match: bool


def _safe_fuzz(a: str, b: str) -> float:
    if not a or not b:
        return 0.0
    if RAPIDFUZZ_AVAILABLE:
        return fuzz.token_sort_ratio(a, b) / 100.0
    a_set, b_set = set(a.lower()), set(b.lower())
    if not a_set or not b_set:
        return 0.0
    return len(a_set & b_set) / len(a_set | b_set)


def _jaro(a: str, b: str) -> float:
    if not a or not b:
        return 0.0
    if JELLYFISH_AVAILABLE:
        return jellyfish.jaro_winkler_similarity(a.lower(), b.lower())
    return 1.0 if a.lower() == b.lower() else 0.0


def score_pair(rec_a: dict[str, Any], rec_b: dict[str, Any]) -> MatchCandidate:
    name_a = f"{rec_a.get('first_name','')} {rec_a.get('last_name','')}".strip()
    name_b = f"{rec_b.get('first_name','')} {rec_b.get('last_name','')}".strip()
    name_score = _safe_fuzz(name_a, name_b) * 0.5 + _jaro(name_a, name_b) * 0.5

    email_a = rec_a.get("email", "").lower().strip()
    email_b = rec_b.get("email", "").lower().strip()
    email_score = 1.0 if email_a and email_a == email_b else _safe_fuzz(email_a, email_b) * 0.3

    phone_a = "".join(c for c in rec_a.get("phone","") if c.isdigit())[-9:]
    phone_b = "".join(c for c in rec_b.get("phone","") if c.isdigit())[-9:]
    phone_score = 1.0 if phone_a and phone_a == phone_b else 0.0

    weighted = name_score * 0.65 + email_score * 0.25 + phone_score * 0.10

    # Name-boost floor: a strong name match can carry the pair
    name_boost_floor = name_score * NAME_BOOST_MULTIPLIER if name_score >= 0.90 else 0.0

    composite = max(weighted, name_boost_floor)

    return MatchCandidate(
        record_a_id=rec_a.get("source_id", ""),
        record_b_id=rec_b.get("source_id", ""),
        composite_score=round(composite, 4),
        name_score=round(name_score, 4),
        email_score=round(email_score, 4),
        phone_score=round(phone_score, 4),
        is_match=composite >= MATCH_THRESHOLD,
    )


def find_candidates(df: pd.DataFrame, sample_size: int = 50) -> list[MatchCandidate]:
    """Naive O(n²) blocking — for demo; production uses LSH or sorted neighbourhood."""
    records = df.head(sample_size).to_dict("records")
    candidates = []
    for i in range(len(records)):
        for j in range(i + 1, len(records)):
            candidate = score_pair(records[i], records[j])
            if candidate.composite_score >= 0.55:
                candidates.append(candidate)
    return sorted(candidates, key=lambda c: c.composite_score, reverse=True)


def build_cluster_ids(matches: list[MatchCandidate]) -> set[str]:
    """
    Transitive cluster: starting from the top match, expand to include any
    record connected to a record already in the cluster.

    A → B (match), B → C (match) ⇒ {A, B, C} cluster, even if A → C wasn't scored.
    """
    if not matches:
        return set()
    cluster_ids: set[str] = {matches[0].record_a_id, matches[0].record_b_id}
    changed = True
    while changed:
        changed = False
        for m in matches:
            if not m.is_match:
                continue
            if m.record_a_id in cluster_ids and m.record_b_id not in cluster_ids:
                cluster_ids.add(m.record_b_id)
                changed = True
            elif m.record_b_id in cluster_ids and m.record_a_id not in cluster_ids:
                cluster_ids.add(m.record_a_id)
                changed = True
    return cluster_ids
