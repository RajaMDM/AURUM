"""
REFINE Survivorship Engine

Three-step processing per attribute:

  1. STANDARDIZE — reverse known dirt patterns (leetspeak, encoding repair,
     casing, accent normalization). A pluggable cleanse layer between raw
     source data and the validator. Real MDM tools have this as a separate
     stage; AURUM bundles it into survivorship via the `standardizer`
     parameter so practitioners can plug in domain-specific rules.

  2. VALIDATE — check the standardized form. Rejects values that remain
     malformed even after standardization (e.g., 12345, !!!, single chars).

  3. SURVIVE — apply the survivorship strategy:
       INDEPENDENT (per-field): first_name, last_name, email, phone
       LINKED TUPLE: (city, country) — mixing produces false geography

Trust score: 0.6 * completeness + 0.4 * source_diversity (3+ sources max).
"""
from __future__ import annotations
from collections.abc import Callable
from typing import Any
import re


TRUST_WEIGHTS: dict[str, float] = {
    "ERP":     1.0,
    "CRM":     0.8,
    "ECOMM":   0.6,
    "LOYALTY": 0.5,
    "WMS":     0.4,
}

_VALID_NAME_CHARS = re.compile(r"[A-Za-z\s\-']")
_LOOKS_LIKE_EMAIL = re.compile(r".+@[a-zA-Z]+\.[a-zA-Z]+")


def standardize_name(value: str) -> str:
    """
    Reverse known name-corruption patterns before validation.

    This is a CLEANSE step that bridges raw source data and the validator.
    In production MDM, swap with domain-specific standardization rules
    (Unicode NFD normalization, accent stripping, casing rules, encoding
    repair for mojibake, organization-specific leetspeak detection, etc.).

    The reference implementation handles dirt patterns AURUM's sample data
    generates. The validator runs AFTER this — so anything still malformed
    after standardization is genuine garbage and gets rejected.
    """
    if not value:
        return value
    cleaned = value.strip()

    # Pattern 1: leetspeak '@' substituted for 'a' — common in obfuscated
    # exports, deliberate masking, or character-encoding incidents.
    # Conservative: only undo when '@' appears in a non-email context.
    if "@" in cleaned and not _LOOKS_LIKE_EMAIL.match(cleaned):
        cleaned = cleaned.replace("@", "a")

    # Pattern 2: trailing punctuation (commas, semicolons from malformed CSV)
    cleaned = cleaned.rstrip(",;:")

    return cleaned.strip()


def _is_valid_name(value: str) -> bool:
    """A name passes if at least 75% of characters are alphabetic, space,
    hyphen or apostrophe. Applied AFTER standardization."""
    if not value:
        return False
    cleaned = value.strip()
    if len(cleaned) < 2:
        return False
    return len(_VALID_NAME_CHARS.findall(cleaned)) / len(cleaned) >= 0.75


def _most_complete_email(values: list[str]) -> str:
    email_re = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", re.IGNORECASE)
    valid = [v.lower().strip() for v in values if email_re.match(v.strip())]
    return valid[0] if valid else ""


def _most_trusted_field(
    cluster: list[dict[str, Any]],
    field: str,
    validator: Callable[[str], bool] | None = None,
    standardizer: Callable[[str], str] | None = None,
) -> str:
    """
    INDEPENDENT survivorship for one field. Pipeline per source:
      raw → standardize → validate → keep if valid
    Then highest-trust valid value wins.
    """
    candidates: list[tuple[float, str]] = []
    for record in cluster:
        src = record.get("source_system", "UNKNOWN")
        trust = TRUST_WEIGHTS.get(src, 0.3)
        raw = record.get(field, "").strip()
        if not raw:
            continue
        value = standardizer(raw) if standardizer else raw
        if validator and not validator(value):
            continue
        candidates.append((trust, value))
    if not candidates:
        return ""
    candidates.sort(key=lambda x: x[0], reverse=True)
    return candidates[0][1]


def _most_trusted_tuple(
    cluster: list[dict[str, Any]],
    fields: list[str],
    field_validators: dict[str, Callable[[str], bool]] | None = None,
) -> dict[str, str]:
    """
    LINKED TUPLE survivorship: the whole tuple comes from one record,
    never composed across records. Used for fields whose mixing would
    produce a false semantic unit (city + country = geographic identity).

    A source qualifies only if ALL listed fields are non-empty AND pass
    any provided validator.
    """
    field_validators = field_validators or {}
    candidates: list[tuple[float, dict[str, str]]] = []

    for record in cluster:
        src = record.get("source_system", "UNKNOWN")
        trust = TRUST_WEIGHTS.get(src, 0.3)
        values = {f: record.get(f, "").strip() for f in fields}

        if not all(values.values()):
            continue

        if not all(
            field_validators[f](v) if f in field_validators else True
            for f, v in values.items()
        ):
            continue

        candidates.append((trust, values))

    if not candidates:
        return {f: "" for f in fields}

    candidates.sort(key=lambda x: x[0], reverse=True)
    return candidates[0][1]


def build_golden_record(cluster: list[dict[str, Any]]) -> dict[str, Any]:
    """
    Merge a cluster of dirty records into one golden record.

    INDEPENDENT survivorship (with standardize → validate → survive):
      first_name, last_name, email, phone
    LINKED TUPLE survivorship:
      (city, country)
    """
    golden: dict[str, Any] = {}
    sources = [r.get("source_system", "UNKNOWN") for r in cluster]
    distinct_sources = list(set(sources))
    golden["source_systems"] = distinct_sources
    golden["cluster_size"] = len(cluster)

    # Names — standardize then validate then survive (independent per field)
    fn = _most_trusted_field(
        cluster, "first_name",
        validator=_is_valid_name,
        standardizer=standardize_name,
    )
    ln = _most_trusted_field(
        cluster, "last_name",
        validator=_is_valid_name,
        standardizer=standardize_name,
    )
    golden["first_name"] = fn.title() if fn else ""
    golden["last_name"]  = ln.title() if ln else ""

    # Email — independent, format-validated
    golden["email"] = _most_complete_email([r.get("email","") for r in cluster])

    # Phone — independent, longest digit string wins
    phones = ["".join(c for c in r.get("phone","") if c.isdigit()) for r in cluster]
    phones = [p for p in phones if p]
    golden["phone"] = max(phones, key=len) if phones else ""

    # Geography — LINKED TUPLE, prevents Dubai-UK frankenrecord
    geo = _most_trusted_tuple(cluster, ["city", "country"])
    golden["city"]    = geo["city"].title()    if geo["city"]    else ""
    golden["country"] = geo["country"].upper() if geo["country"] else ""

    # Trust score
    key_fields = ["first_name", "last_name", "email", "phone", "city", "country"]
    filled = sum(1 for f in key_fields if golden.get(f, "").strip())
    completeness = filled / len(key_fields)
    diversity    = min(len(distinct_sources) / 3, 1.0)

    golden["trust_score"] = round(0.6 * completeness + 0.4 * diversity, 2)
    golden["trust_components"] = {
        "completeness":     round(completeness, 2),
        "source_diversity": round(diversity, 2),
    }
    golden["is_golden"] = golden["trust_score"] >= 0.6

    return golden
