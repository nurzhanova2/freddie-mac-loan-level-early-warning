#!/usr/bin/env python3
"""Evaluate frozen v01 logistic and XGBoost models on Q3 control samples."""

from __future__ import annotations

import argparse
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.calibration import calibration_curve
from sklearn.metrics import average_precision_score, brier_score_loss, roc_auc_score


NUMERIC = ['original_interest_rate','original_upb','original_loan_term','original_loan_to_value_ratio_ltv','original_combined_loan_to_value_ratio_cltv','number_of_borrowers','debt_to_income_dti','borrower_credit_score_at_origination','co_borrower_credit_score_at_origination','mortgage_insurance_percentage','current_interest_rate','current_actual_upb','loan_age','remaining_months_to_legal_maturity','remaining_months_to_maturity']
CATEGORICAL = ['channel','first_time_home_buyer_indicator','loan_purpose','property_type','number_of_units','occupancy_status','property_state','amortization_type','current_loan_delinquency_status','modification_flag']
FEATURES = NUMERIC + CATEGORICAL
MODELS = ("logistic", "xgboost")


def predict(model, calibrator, frame: pd.DataFrame) -> np.ndarray:
    values = []
    for start in range(0, len(frame), 100_000):
        raw = model.predict_proba(frame.iloc[start:start + 100_000][FEATURES])[:, 1]
        values.append(calibrator.predict(raw))
    return np.concatenate(values)


def metric_row(target: str, model_name: str, scope: str, y: pd.Series, score: np.ndarray) -> dict[str, object]:
    return {
        "target": target, "model": model_name, "scope": scope, "rows": len(y), "events": int(y.sum()),
        "event_rate_pct": round(float(y.mean() * 100), 5),
        "roc_auc": round(float(roc_auc_score(y, score)), 6),
        "pr_auc": round(float(average_precision_score(y, score)), 6),
        "brier_calibrated": round(float(brier_score_loss(y, score)), 6),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", choices=("formal_adverse_6m", "early_deterioration_6m"), required=True)
    parser.add_argument("--samples-dir", type=Path, default=Path("fannie_mae/data/q3_control_samples_v01"))
    parser.add_argument("--models-root", type=Path, default=Path("fannie_mae/models"))
    parser.add_argument("--reports-dir", type=Path, default=Path("fannie_mae/reports/q3_fixed_models_v01"))
    args = parser.parse_args()
    args.reports_dir.mkdir(parents=True, exist_ok=True)
    frame = pd.read_parquet(args.samples_dir / f"{args.target}_q3_control_sample_v01.parquet")
    summary, reliability = [], []
    alert_frames = []
    capacity = 0.01 if args.target == "formal_adverse_6m" else 0.05
    for model_name in MODELS:
        model_dir = args.models_root / f"{model_name}_v01"
        model = joblib.load(model_dir / f"{args.target}_{model_name}_v01.joblib")
        calibrator_name = (
            f"{args.target}_isotonic_calibrator_v01.joblib"
            if model_name == "logistic" else f"{args.target}_{model_name}_isotonic_calibrator_v01.joblib"
        )
        calibrator = joblib.load(model_dir / calibrator_name)
        score = predict(model, calibrator, frame)
        summary.append(metric_row(args.target, model_name, "all_q3", frame.label, score))
        for cohort, index in frame.groupby("acquisition_cohort", sort=True).groups.items():
            subset = frame.loc[index]
            summary.append(metric_row(args.target, model_name, cohort, subset.label, score[index.to_numpy()]))
        observed, predicted = calibration_curve(frame.label, score, n_bins=10, strategy="quantile")
        reliability.extend({"target": args.target, "model": model_name, "bin": i + 1, "mean_predicted_probability": p, "observed_event_rate": o} for i, (p, o) in enumerate(zip(predicted, observed)))
        alerts = frame[["loan_identifier", "monthly_reporting_period", "acquisition_cohort", "label"]].copy()
        alerts["score"] = score
        alerts = alerts.sort_values(["score", "loan_identifier", "monthly_reporting_period"], ascending=[False, True, True], kind="mergesort")
        selected = alerts.iloc[:max(1, round(len(alerts) * capacity))].copy()
        tp = int(selected.label.sum())
        summary.append({
            "target": args.target, "model": model_name, "scope": f"all_q3_top_{capacity:.0%}", "rows": len(selected),
            "events": tp, "event_rate_pct": round(float(selected.label.mean() * 100), 5),
            "roc_auc": None, "pr_auc": None, "brier_calibrated": None,
            "precision_pct": round(100 * tp / len(selected), 5),
            "recall_pct": round(100 * tp / int(frame.label.sum()), 5),
            "threshold_score": float(selected.score.iloc[-1]),
        })
        selected["model"] = model_name
        selected["capacity"] = capacity
        alert_frames.append(selected)
    pd.DataFrame(summary).to_csv(args.reports_dir / f"{args.target}_q3_fixed_model_metrics_v01.csv", index=False)
    pd.DataFrame(reliability).to_csv(args.reports_dir / f"{args.target}_q3_fixed_model_calibration_v01.csv", index=False)
    pd.concat(alert_frames, ignore_index=True).to_parquet(args.reports_dir / f"{args.target}_q3_fixed_model_alerts_v01.parquet", index=False)


if __name__ == "__main__":
    main()
