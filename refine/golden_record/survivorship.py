"""
REFINE Survivorship Engine
Given a cluster of matched records, applies survivorship rules to
produce a single golden record with maximum trusted attribute coverage.
"""
from __future__ import annotations
from typing import Any
import re


TRUST_WEIGHTS: dict[str, float] = {
    "ERP":    1.0,
    "CRM":    0.8,
    "ECOMM":  0.6,
    "LOYALTY":0.5,
    "WMS":    0.4,
}


def _clean(value: str) -> str:
    return value.strip().rstrip(",").strip()


def _most_trusted(values_by_source: list[tuple[str, str]]) -> str:
    """Return the value from the highest-trust source."""
    sorted_vals = sorted(
        [(TRUST_WEIGHTS.get(src, 0.3), val) for src, val in values_by_source if val.strip()],
        reverse=True,
    )
    return _clean(sorted_vals[0][1]) if sorted_vals else ""


def _most_complete_email(values: list[str]) -> str:
    email_re = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", re.IGNORECASE)
    valid = [v.lower().strip() for v in values if email_re.match(v.strip())]
    return valid[0] if valid else ""


def build_golden_record(cluster: list[dict[str, Any]]) -> dict[str, Any]:
    """
    Merge a cluster of dirty records into one golden record.
    cluster: list of dicts, each with a 'source_system' key.
    """
    golden: dict[str, Any] = {}
    sources = [r.get("source_system", "UNKNOWN") for r in cluster]
    golden["source_systems"] = list(set(sources))
    golden["cluster_size"] = len(cluster)

    # Name: most trusted source
    golden["first_name"] = _most_trusted([
        (r.get("source_system",""), r.get("first_name","").title()) for r in cluster
    ])
    golden["last_name"] = _most_trusted([
        (r.get("source_system",""), r.get("last_name","").title()) for r in cluster
    ])

    # Email: most complete (valid format wins)
    golden["email"] = _most_complete_email([r.get("email","") for r in cluster])

    # Phone: longest digit string (most complete)
    phones = ["".join(c for c in r.get("phone","") if c.isdigit()) for r in cluster]
    phones = [p for p in phones if p]
    golden["phone"] = max(phones, key=len) if phones else ""

    # City / Country: most trusted
    golden["city"] = _most_trusted([
        (r.get("source_system",""), r.get("city","").title()) for r in cluster
    ])
    golden["country"] = _most_trusted([
        (r.get("source_system",""), r.get("country","").upper()) for r in cluster
    ])

    # Trust score: coverage of key fields
    key_fields = ["first_name","last_name","email","phone","city","country"]
    filled = sum(1 for f in key_fields if golden.get(f,"").strip())
    golden["trust_score"] = round(filled / len(key_fields), 2)
    golden["is_golden"] = True

    return golden
