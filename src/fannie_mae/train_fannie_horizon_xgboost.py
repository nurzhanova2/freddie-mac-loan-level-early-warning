#!/usr/bin/env python3
"""Fit a fixed 1% natural-rate XGBoost model for one forecast horizon."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.isotonic import IsotonicRegression
from sklearn.metrics import average_precision_score, brier_score_loss, roc_auc_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OrdinalEncoder
from xgboost import XGBClassifier


TARGETS = (
    "formal_adverse_3m", "formal_adverse_6m", "formal_adverse_12m",
    "early_deterioration_3m", "early_deterioration_6m", "early_deterioration_12m",
)
NUMERIC = ["original_interest_rate", "original_upb", "original_loan_term", "original_loan_to_value_ratio_ltv", "original_combined_loan_to_value_ratio_cltv", "number_of_borrowers", "debt_to_income_dti", "borrower_credit_score_at_origination", "co_borrower_credit_score_at_origination", "mortgage_insurance_percentage", "current_interest_rate", "current_actual_upb", "loan_age", "remaining_months_to_legal_maturity", "remaining_months_to_maturity"]
CATEGORICAL = ["channel", "first_time_home_buyer_indicator", "loan_purpose", "property_type", "number_of_units", "occupancy_status", "property_state", "amortization_type", "current_loan_delinquency_status", "modification_flag"]
FEATURES = NUMERIC + CATEGORICAL


def metrics(y: pd.Series, probability) -> dict[str, float]:
    return {
        "roc_auc": round(float(roc_auc_score(y, probability)), 6),
        "pr_auc": round(float(average_precision_score(y, probability)), 6),
        "brier_score": round(float(brier_score_loss(y, probability)), 6),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", choices=TARGETS, required=True)
    parser.add_argument("--samples-dir", type=Path, default=Path("fannie_mae/data/horizon_sensitivity_v01"))
    parser.add_argument("--output-dir", type=Path, default=Path("fannie_mae/models/horizon_sensitivity_v01"))
    args = parser.parse_args()
    train = pd.read_parquet(args.samples_dir / f"{args.target}_train_sample_v01.parquet")
    validation = pd.read_parquet(args.samples_dir / f"{args.target}_validation_sample_v01.parquet")
    if not (train.split == "train").all() or not (validation.split == "validation").all():
        raise ValueError("Expected fixed train and validation split labels")
    preprocess = ColumnTransformer([
        ("num", SimpleImputer(strategy="median"), NUMERIC),
        ("cat", Pipeline([
            ("impute", SimpleImputer(strategy="most_frequent")),
            ("ordinal", OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1, encoded_missing_value=-1)),
        ]), CATEGORICAL),
    ])
    estimator = XGBClassifier(
        n_estimators=160, max_depth=6, learning_rate=0.08, min_child_weight=10,
        subsample=0.8, colsample_bytree=0.8, objective="binary:logistic",
        eval_metric="logloss", tree_method="hist", n_jobs=4, random_state=42,
    )
    model = Pipeline([("preprocess", preprocess), ("model", estimator)])
    model.fit(train[FEATURES], train.label)
    raw = model.predict_proba(validation[FEATURES])[:, 1]
    calibrator = IsotonicRegression(out_of_bounds="clip").fit(raw, validation.label)
    calibrated = calibrator.predict(raw)
    output = args.output_dir / args.target
    output.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, output / "model.joblib")
    joblib.dump(calibrator, output / "isotonic_calibrator.joblib")
    report = {
        "target": args.target,
        "train_sample": str(args.samples_dir / f"{args.target}_train_sample_v01.parquet"),
        "validation_sample": str(args.samples_dir / f"{args.target}_validation_sample_v01.parquet"),
        "training_rows": int(len(train)), "training_events": int(train.label.sum()),
        "training_event_rate_pct": round(float(train.label.mean() * 100), 6),
        "validation_rows": int(len(validation)), "validation_events": int(validation.label.sum()),
        "validation_raw": metrics(validation.label, raw),
        "validation_isotonic_calibrated": metrics(validation.label, calibrated),
        "oot_accessed": False,
        "hyperparameters": estimator.get_params(),
    }
    (output / "fit_and_calibration_manifest.json").write_text(json.dumps(report, indent=2, default=str) + "\n")
    print(f"FIT {args.target}: {len(train):,} train rows; {len(validation):,} validation rows", flush=True)


if __name__ == "__main__":
    main()
