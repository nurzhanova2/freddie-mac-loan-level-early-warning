#!/usr/bin/env python3
"""Create a de-identified approved alert export from frozen Fannie OOT scores.

The output deliberately excludes raw loan identifiers, raw features, and
training records.  It is intended solely for the local research prototype,
where the observed outcome is retained as a *post-window audit field* and is
never supplied to the predictive model.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import xgboost as xgb

from evaluate_fannie_alert_policy import FEATURES


SPECS = (
    ("formal_adverse_6m", "Red", 0.01, "FA"),
    ("early_deterioration_6m", "Amber", 0.05, "ED"),
)


def top_positive_shap(model, frame: pd.DataFrame) -> tuple[np.ndarray, np.ndarray]:
    """Return a readable leading risk-increasing TreeSHAP driver per alert."""
    transformed = model.named_steps["preprocess"].transform(frame[FEATURES])
    names = np.asarray(model.named_steps["preprocess"].get_feature_names_out())
    values = model.named_steps["model"].get_booster().predict(
        xgb.DMatrix(transformed, feature_names=list(names)), pred_contribs=True
    )[:, :-1]
    positive = np.maximum(values, 0)
    indices = positive.argmax(axis=1)
    contributions = positive[np.arange(len(frame)), indices]
    # A rare all-negative explanation remains interpretable through its largest
    # absolute contribution rather than an invented positive contribution.
    missing = contributions == 0
    if missing.any():
        absolute = np.abs(values[missing])
        fallback = absolute.argmax(axis=1)
        indices[missing] = fallback
        contributions[missing] = values[missing, fallback]
    readable = np.char.replace(np.char.replace(names[indices].astype(str), "num__", ""), "cat__", "")
    return readable, contributions


def make_export(target: str, tier: str, capacity: float, prefix: str, samples_dir: Path, models_dir: Path) -> pd.DataFrame:
    frame = pd.read_parquet(samples_dir / f"{target}_out_of_time_test_sample_v01.parquet")
    model = joblib.load(models_dir / f"{target}_xgboost_v01.joblib")
    calibrator = joblib.load(models_dir / f"{target}_xgboost_isotonic_calibrator_v01.joblib")
    frame["risk_score"] = calibrator.predict(model.predict_proba(frame[FEATURES])[:, 1])
    frame = frame.sort_values(
        ["risk_score", "loan_identifier", "monthly_reporting_period"],
        ascending=[False, True, True],
        kind="mergesort",
    ).reset_index(drop=True)
    count = max(1, round(len(frame) * capacity))
    alerts = frame.iloc[:count].copy()
    threshold = float(alerts.risk_score.iloc[-1])
    drivers, contributions = top_positive_shap(model, alerts)
    reporting_month = pd.to_datetime(alerts.monthly_reporting_period)
    # This is the end of the already-complete six-month label window, not an
    # event date.  It makes the audit timing explicit without exposing history.
    observed_at = (reporting_month + pd.DateOffset(months=6)).dt.strftime("%Y-%m")
    return pd.DataFrame(
        {
            "alert_id": [f"FNN-{prefix}-{rank:06d}" for rank in range(1, len(alerts) + 1)],
            "loan_reference": [f"CASE-{prefix}-{rank:06d}" for rank in range(1, len(alerts) + 1)],
            "cohort": alerts.acquisition_cohort.to_numpy(),
            "reporting_month": reporting_month.dt.strftime("%Y-%m").to_numpy(),
            "target": target,
            "risk_score": alerts.risk_score.to_numpy(),
            "trigger_threshold": threshold,
            "tier": tier,
            "top_shap_driver": drivers,
            "top_shap_contribution": contributions,
            "review_status": "Pending",
            "observed_outcome": alerts.label.astype(int).to_numpy(),
            "outcome_observed_at": observed_at.to_numpy(),
        }
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--samples-dir", type=Path, default=Path("fannie_mae/data/model_samples_v01"))
    parser.add_argument("--models-dir", type=Path, default=Path("fannie_mae/models/xgboost_v01"))
    parser.add_argument("--output", type=Path, default=Path("src/prototype/api/approved_exports/fannie_q1_oot_safe_alert_export_v01.csv"))
    args = parser.parse_args()
    output = args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    export = pd.concat([make_export(*spec, args.samples_dir, args.models_dir) for spec in SPECS], ignore_index=True)
    export.to_csv(output, index=False, float_format="%.8f")
    print(f"Wrote {len(export):,} de-identified research alerts to {output}")


if __name__ == "__main__":
    main()
