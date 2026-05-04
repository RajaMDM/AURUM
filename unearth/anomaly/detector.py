"""
UNEARTH ML Anomaly Detector
Isolation-Forest-based detector that flags rows whose feature combinations
are unlike the rest of the dataset.

The detector operates on CSV input with generic feature engineering that
works across all 7 AURUM domains. Per-domain feature tuning is a v0.3.0
enhancement; this v0.1.3 baseline catches the high-value cases (sudden
length shifts, character-class anomalies, multi-field empty patterns)
without requiring domain knowledge.

Determinism: `random_state` is fixed at construction time so the same
input produces the same output across runs — required for steward audit.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest

logger = logging.getLogger(__name__)


@dataclass
class FlaggedRow:
    """A single row that the detector marks as anomalous."""
    row_index: int
    anomaly_score: float            # -1 (most anomalous) to ~0.5 (most normal)
    feature_signal: dict[str, Any]  # the row's most-unusual numeric features

    def to_dict(self) -> dict[str, Any]:
        return {
            "row_index": self.row_index,
            "anomaly_score": round(self.anomaly_score, 4),
            "feature_signal": self.feature_signal,
        }


@dataclass
class AnomalyResult:
    domain: str
    row_count: int
    flagged: list[FlaggedRow] = field(default_factory=list)
    contamination: float = 0.1
    feature_columns: list[str] = field(default_factory=list)

    @property
    def flagged_count(self) -> int:
        return len(self.flagged)

    @property
    def flagged_pct(self) -> float:
        if self.row_count == 0:
            return 0.0
        return round(self.flagged_count / self.row_count * 100, 1)

    def summary(self) -> dict[str, Any]:
        return {
            "domain": self.domain,
            "rows": self.row_count,
            "flagged": self.flagged_count,
            "flagged_pct": self.flagged_pct,
            "contamination": self.contamination,
            "feature_count": len(self.feature_columns),
            "top_flagged": [f.to_dict() for f in self.flagged[:5]],
        }


class AnomalyDetector:
    """Isolation-Forest anomaly detector with generic feature engineering.

    Parameters
    ----------
    contamination
        Expected fraction of anomalous rows. ``"auto"`` lets sklearn pick;
        a float in (0, 0.5) sets an explicit budget. Default 0.1 (10%).
    n_estimators
        Number of trees in the forest. More trees = more stable scores.
    random_state
        RNG seed — fixed for reproducibility across runs.
    """

    MIN_ROWS = 10  # Isolation Forest is unreliable below this

    def __init__(
        self,
        contamination: float | str = 0.1,
        n_estimators: int = 100,
        random_state: int = 42,
    ) -> None:
        self.contamination = contamination
        self.n_estimators = n_estimators
        self.random_state = random_state

    def detect(self, path: str, domain: str = "generic") -> AnomalyResult:
        """Run anomaly detection on a CSV file.

        Returns an ``AnomalyResult`` listing flagged rows with their scores
        and the features that drove the flag. If the file has fewer than
        ``MIN_ROWS`` rows, returns an empty result with a warning logged.
        """
        df = pd.read_csv(path, dtype=str, keep_default_na=False)
        result = AnomalyResult(
            domain=domain,
            row_count=len(df),
            contamination=self.contamination if isinstance(self.contamination, float) else 0.1,
        )

        if len(df) < self.MIN_ROWS:
            logger.warning(
                "AnomalyDetector: %d rows is below MIN_ROWS=%d — skipping detection.",
                len(df), self.MIN_ROWS,
            )
            return result

        feature_df = self._engineer_features(df)
        if feature_df.empty or feature_df.shape[1] == 0:
            logger.warning("AnomalyDetector: no features extracted — skipping detection.")
            return result

        result.feature_columns = list(feature_df.columns)

        model = IsolationForest(
            contamination=self.contamination,
            n_estimators=self.n_estimators,
            random_state=self.random_state,
        )
        predictions = model.fit_predict(feature_df.values)
        scores = model.score_samples(feature_df.values)

        flagged_indices = np.where(predictions == -1)[0]
        for idx in flagged_indices:
            row_features = feature_df.iloc[idx].to_dict()
            top_features = self._select_outlier_features(row_features, feature_df)
            result.flagged.append(
                FlaggedRow(
                    row_index=int(idx),
                    anomaly_score=float(scores[idx]),
                    feature_signal=top_features,
                )
            )

        # Sort flagged rows by anomaly score (most anomalous first)
        result.flagged.sort(key=lambda f: f.anomaly_score)
        return result

    @staticmethod
    def _engineer_features(df: pd.DataFrame) -> pd.DataFrame:
        """Generic per-column feature engineering.

        For each text column produces six numeric features capturing length,
        character composition, and null state. Columns that are entirely
        empty across the dataset contribute no signal and are dropped.
        """
        features: dict[str, np.ndarray] = {}

        for col in df.columns:
            series = df[col].fillna("").astype(str)
            if (series == "").all():
                continue

            features[f"{col}__is_empty"] = (series == "").astype(int).values
            features[f"{col}__length"] = series.str.len().values
            features[f"{col}__digit_ratio"] = series.apply(
                lambda v: sum(c.isdigit() for c in v) / max(len(v), 1)
            ).values
            features[f"{col}__alpha_ratio"] = series.apply(
                lambda v: sum(c.isalpha() for c in v) / max(len(v), 1)
            ).values
            features[f"{col}__special_ratio"] = series.apply(
                lambda v: sum(not c.isalnum() and not c.isspace() for c in v) / max(len(v), 1)
            ).values
            features[f"{col}__upper_ratio"] = series.apply(
                lambda v: sum(c.isupper() for c in v) / max(sum(c.isalpha() for c in v), 1)
            ).values

        if not features:
            return pd.DataFrame()

        # Row-level summary features
        feature_df = pd.DataFrame(features)
        is_empty_cols = [c for c in feature_df.columns if c.endswith("__is_empty")]
        if is_empty_cols:
            feature_df["__row_empty_count"] = feature_df[is_empty_cols].sum(axis=1).values

        return feature_df.astype(float)

    @staticmethod
    def _select_outlier_features(
        row_features: dict[str, float],
        full_features: pd.DataFrame,
        top_k: int = 3,
    ) -> dict[str, Any]:
        """For one flagged row, return the top_k features that deviate most
        from the dataset's per-feature mean (z-score in absolute value).
        """
        means = full_features.mean()
        stds = full_features.std().replace(0, 1)  # avoid div-by-zero
        z_scores = {col: abs((row_features[col] - means[col]) / stds[col]) for col in full_features.columns}
        top = sorted(z_scores.items(), key=lambda kv: kv[1], reverse=True)[:top_k]
        return {col: round(z, 2) for col, z in top}
