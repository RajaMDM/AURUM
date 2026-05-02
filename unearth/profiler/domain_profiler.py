"""
UNEARTH Domain Profiler
Runs completeness, consistency, and format checks across a domain dataset.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any
import pandas as pd
import re


@dataclass
class DQIssue:
    row_index: int
    field: str
    rule: str
    value: Any
    severity: str = "WARNING"


@dataclass
class ProfileResult:
    domain: str
    row_count: int
    issues: list[DQIssue] = field(default_factory=list)

    @property
    def issue_count(self) -> int:
        return len(self.issues)

    @property
    def quality_score(self) -> float:
        if self.row_count == 0:
            return 0.0
        clean_rows = self.row_count - len({i.row_index for i in self.issues})
        return round(clean_rows / self.row_count * 100, 1)

    def summary(self) -> dict[str, Any]:
        return {
            "domain": self.domain,
            "rows": self.row_count,
            "issues": self.issue_count,
            "quality_score_pct": self.quality_score,
            "by_rule": self._by_rule(),
        }

    def _by_rule(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for issue in self.issues:
            counts[issue.rule] = counts.get(issue.rule, 0) + 1
        return counts


class CustomerProfiler:
    """DQ rules specific to the Customer domain."""

    EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", re.IGNORECASE)
    PHONE_RE = re.compile(r"^[\+\d\-\(\)\s]{7,20}$")

    def profile(self, path: str) -> ProfileResult:
        df = pd.read_csv(path, dtype=str, keep_default_na=False)
        result = ProfileResult(domain="customer", row_count=len(df))

        for i, row in df.iterrows():
            # Completeness
            for req in ["first_name", "last_name"]:
                if req in df.columns and row.get(req, "").strip() == "":
                    result.issues.append(DQIssue(i, req, "MISSING_REQUIRED", "", "ERROR"))

            # Email format
            email = row.get("email", "").strip()
            if email and not self.EMAIL_RE.match(email):
                result.issues.append(DQIssue(i, "email", "INVALID_EMAIL_FORMAT", email))

            # Phone format
            phone = row.get("phone", "").strip()
            if phone and not self.PHONE_RE.match(phone):
                result.issues.append(DQIssue(i, "phone", "INVALID_PHONE_FORMAT", phone))

            # Case consistency check
            fname = row.get("first_name", "")
            if fname and fname == fname.upper() and len(fname) > 2:
                result.issues.append(DQIssue(i, "first_name", "ALL_CAPS", fname, "WARNING"))

        return result
