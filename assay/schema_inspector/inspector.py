"""
ASSAY Schema Inspector
Profiles an incoming CSV/dataset: field types, nulls, cardinality, format patterns.
The first thing you do before touching source data.
"""
from __future__ import annotations
import re
from pathlib import Path
from typing import Any
import pandas as pd


class FieldProfile:
    def __init__(self, name: str, series: pd.Series) -> None:
        self.name = name
        self.total = len(series)
        self.null_count = series.isna().sum() + (series == "").sum()
        self.null_pct = round(self.null_count / self.total * 100, 1)
        self.cardinality = series.nunique()
        self.sample_values = series.dropna().head(3).tolist()
        self.inferred_type = self._infer(series)

    def _infer(self, s: pd.Series) -> str:
        non_null = s.dropna().astype(str).str.strip()
        non_null = non_null[non_null != ""]
        if non_null.empty:
            return "empty"
        email_pct = non_null.str.contains(r"@.*\.", regex=True).mean()
        if email_pct > 0.5:
            return "email"
        phone_pct = non_null.str.contains(r"[\d\-\+\(\)]{7,}", regex=True).mean()
        if phone_pct > 0.6:
            return "phone"
        date_pct = non_null.str.contains(r"\d{4}[-/]\d{2}[-/]\d{2}", regex=True).mean()
        if date_pct > 0.4:
            return "date"
        try:
            pd.to_numeric(non_null)
            return "numeric"
        except Exception:
            pass
        return "text"

    def to_dict(self) -> dict[str, Any]:
        return {
            "field": self.name,
            "null_pct": self.null_pct,
            "cardinality": self.cardinality,
            "inferred_type": self.inferred_type,
            "samples": self.sample_values,
        }


class SchemaInspector:
    """Assay a source dataset — understand its structure before ingestion."""

    def __init__(self, source_name: str) -> None:
        self.source_name = source_name
        self.profiles: list[FieldProfile] = []

    def inspect(self, path: str | Path) -> dict[str, Any]:
        df = pd.read_csv(path, dtype=str, keep_default_na=False)
        self.profiles = [FieldProfile(col, df[col]) for col in df.columns]
        return {
            "source": self.source_name,
            "row_count": len(df),
            "field_count": len(df.columns),
            "fields": [p.to_dict() for p in self.profiles],
            "high_null_fields": [p.name for p in self.profiles if p.null_pct > 30],
            "low_cardinality_fields": [p.name for p in self.profiles if p.cardinality <= 5],
        }
