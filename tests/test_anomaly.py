"""
Unit tests for the UNEARTH ML anomaly detector.

The detector should flag rows whose feature combinations are unlike the rest.
We construct datasets where one or two rows are obviously different (very
long values, unusual character classes, all-empty fields) and assert the
detector finds them.
"""
from __future__ import annotations
import tempfile
from pathlib import Path

import pytest

from unearth.anomaly import AnomalyDetector, AnomalyResult, FlaggedRow


def _write_csv(rows: list[str]) -> str:
    tmp = tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False, newline="")
    tmp.write("\n".join(rows) + "\n")
    tmp.close()
    return tmp.name


def test_detector_flags_obvious_outlier_in_clean_dataset():
    rows = ["first_name,last_name,email,phone"]
    # 19 typical rows
    for i in range(19):
        rows.append(f"John{i},Smith{i},john{i}@acme.com,+97150{i:07d}")
    # 1 wildly different row — empty everything
    rows.append(",,,")

    path = _write_csv(rows)
    result = AnomalyDetector(contamination=0.1, random_state=42).detect(path, domain="customer")

    assert isinstance(result, AnomalyResult)
    assert result.row_count == 20
    assert result.flagged_count >= 1, "expected at least the all-empty row to be flagged"
    flagged_indices = {f.row_index for f in result.flagged}
    assert 19 in flagged_indices, "the deliberately empty row was not flagged"
    Path(path).unlink()


def test_detector_returns_empty_for_small_datasets():
    """Datasets below MIN_ROWS should return an empty result with no crash."""
    rows = ["col_a,col_b"] + ["x,y"] * 5  # 5 data rows — below MIN_ROWS=10
    path = _write_csv(rows)
    result = AnomalyDetector().detect(path, domain="customer")
    assert result.row_count == 5
    assert result.flagged_count == 0
    assert result.feature_columns == []  # detection skipped
    Path(path).unlink()


def test_detector_summary_shape():
    rows = ["first_name,last_name,email"]
    for i in range(15):
        rows.append(f"John{i},Smith{i},john{i}@acme.com")
    rows.append(",,")  # one outlier

    path = _write_csv(rows)
    result = AnomalyDetector(contamination=0.1).detect(path, domain="customer")
    summary = result.summary()

    assert summary["domain"] == "customer"
    assert summary["rows"] == 16
    assert summary["flagged"] >= 1
    assert summary["flagged_pct"] > 0
    assert summary["feature_count"] > 0
    assert isinstance(summary["top_flagged"], list)
    if summary["top_flagged"]:
        first = summary["top_flagged"][0]
        assert "row_index" in first
        assert "anomaly_score" in first
        assert "feature_signal" in first
    Path(path).unlink()


def test_detector_is_deterministic():
    rows = ["col_a,col_b"]
    for i in range(20):
        rows.append(f"value{i},data{i}")
    rows.append("WILDLY_DIFFERENT_LONG_OUTLIER_!@#$%^&*,xxxxxxxxxxxxxxxxxxxxxx")

    path = _write_csv(rows)
    a = AnomalyDetector(contamination=0.1, random_state=42).detect(path)
    b = AnomalyDetector(contamination=0.1, random_state=42).detect(path)

    assert a.flagged_count == b.flagged_count
    assert {f.row_index for f in a.flagged} == {f.row_index for f in b.flagged}
    Path(path).unlink()


def test_detector_handles_all_empty_column():
    """Columns that are 100% empty should be silently dropped from features."""
    rows = ["col_a,col_b,col_c"]
    for i in range(15):
        rows.append(f"value{i},data{i},")  # col_c always empty

    path = _write_csv(rows)
    result = AnomalyDetector().detect(path)
    # Feature columns should not include col_c features
    assert not any(c.startswith("col_c__") for c in result.feature_columns), \
        "all-empty column should be excluded from feature engineering"
    Path(path).unlink()


def test_flagged_row_serializable():
    flagged = FlaggedRow(row_index=5, anomaly_score=-0.42, feature_signal={"col__length": 3.7})
    d = flagged.to_dict()
    assert d == {"row_index": 5, "anomaly_score": -0.42, "feature_signal": {"col__length": 3.7}}
