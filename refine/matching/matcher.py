"""
REFINE Matcher
Fuzzy matching engine using RapidFuzz + Jaro-Winkler + token scoring.
Produces match candidates with confidence scores for survivorship.
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
    # Fallback: simple char overlap
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
    name_score  = _safe_fuzz(name_a, name_b) * 0.5 + _jaro(name_a, name_b) * 0.5

    email_a = rec_a.get("email", "").lower().strip()
    email_b = rec_b.get("email", "").lower().strip()
    email_score = 1.0 if email_a and email_a == email_b else _safe_fuzz(email_a, email_b) * 0.3

    phone_a = "".join(c for c in rec_a.get("phone","") if c.isdigit())[-9:]
    phone_b = "".join(c for c in rec_b.get("phone","") if c.isdigit())[-9:]
    phone_score = 1.0 if phone_a and phone_a == phone_b else 0.0

    composite = name_score * 0.5 + email_score * 0.35 + phone_score * 0.15

    return MatchCandidate(
        record_a_id=rec_a.get("source_id", ""),
        record_b_id=rec_b.get("source_id", ""),
        composite_score=round(composite, 4),
        name_score=round(name_score, 4),
        email_score=round(email_score, 4),
        phone_score=round(phone_score, 4),
        is_match=composite >= 0.75,
    )


def find_candidates(df: pd.DataFrame, sample_size: int = 30) -> list[MatchCandidate]:
    """Naive O(n²) blocking — for demo; production uses LSH or sorted neighbourhood."""
    records = df.head(sample_size).to_dict("records")
    candidates = []
    for i in range(len(records)):
        for j in range(i + 1, len(records)):
            candidate = score_pair(records[i], records[j])
            if candidate.composite_score >= 0.6:
                candidates.append(candidate)
    return sorted(candidates, key=lambda c: c.composite_score, reverse=True)
