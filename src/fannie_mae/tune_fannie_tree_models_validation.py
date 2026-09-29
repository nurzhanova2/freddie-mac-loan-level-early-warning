#!/usr/bin/env python3
"""Select pre-registered tree specifications using train and validation only.

The script intentionally has no OOT input argument and does not open the OOT
file. It compares frozen baseline specifications with a compact, documented
regularised candidate set on the same Q1+Q3 train/validation samples.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import joblib
import pandas as pd
import yaml
from catboost import CatBoostClassifier
from lightgbm import LGBMClassifier
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.metrics import average_precision_score, brier_score_loss, roc_auc_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OrdinalEncoder
from xgboost import XGBClassifier


NUMERIC = [
    "original_interest_rate", "original_upb", "original_loan_term", "original_loan_to_value_ratio_ltv",
    "original_combined_loan_to_value_ratio_cltv", "number_of_borrowers", "debt_to_income_dti",
    "borrower_credit_score_at_origination", "co_borrower_credit_score_at_origination",
    "mortgage_insurance_percentage", "current_interest_rate", "current_actual_upb", "loan_age",
    "remaining_months_to_legal_maturity", "remaining_months_to_maturity",
]
CATEGORICAL = [
    "channel", "first_time_home_buyer_indicator", "loan_purpose", "property_type", "number_of_units",
    "occupancy_status", "property_state", "amortization_type", "current_loan_delinquency_status", "modification_flag",
]
FEATURES = NUMERIC + CATEGORICAL


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", choices=["formal_adverse_6m", "early_deterioration_6m"], required=True)
    parser.add_argument("--algorithm", choices=["xgboost", "catboost", "lightgbm", "all"], default="all")
    parser.add_argument(
        "--config", type=Path,
        default=Path("fannie_mae/config/fannie_tree_hyperparameter_selection_v01.yml"),
    )
    parser.add_argument("--output-dir", type=Path, default=Path("fannie_mae/models/tuned_trees_validation_v01"))
    parser.add_argument(
        "--summary-dir", type=Path,
        default=Path("fannie_mae/reports/tree_hyperparameter_selection_v01"),
    )
    parser.add_argument(
        "--rescore-only",
        action="store_true",
        help="Recreate validation metrics from saved candidate models without fitting or reading OOT.",
    )
    return parser.parse_args()


def make_preprocessor() -> ColumnTransformer:
    return ColumnTransformer([
        ("num", SimpleImputer(strategy="median"), NUMERIC),
        ("cat", Pipeline([
            ("impute", SimpleImputer(strategy="most_frequent")),
            ("ordinal", OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1, encoded_missing_value=-1)),
        ]), CATEGORICAL),
    ])


def make_estimator(algorithm: str, parameters: dict[str, object], seed: int, thread_limit: int):
    if algorithm == "xgboost":
        return XGBClassifier(
            **parameters, objective="binary:logistic", eval_metric="logloss", tree_method="hist",
            n_jobs=thread_limit, random_state=seed,
        )
    if algorithm == "catboost":
        return CatBoostClassifier(
            **parameters, loss_function="Logloss", verbose=False, random_seed=seed, thread_count=thread_limit,
        )
    return LGBMClassifier(
        **parameters, random_state=seed, n_jobs=thread_limit, verbosity=-1,
    )


def score(y: pd.Series, probability) -> dict[str, float]:
    return {
        "roc_auc": float(roc_auc_score(y, probability)),
        "pr_auc": float(average_precision_score(y, probability)),
        "brier_uncalibrated": float(brier_score_loss(y, probability)),
    }


def main() -> None:
    args = parse_args()
    config = yaml.safe_load(args.config.read_text())
    samples_dir = Path(config["data"]["samples_dir"])
    train = pd.read_parquet(samples_dir / f"{args.target}_train_sample_v01.parquet")
    validation = pd.read_parquet(samples_dir / f"{args.target}_validation_sample_v01.parquet")
    algorithms = list(config["candidates"]) if args.algorithm == "all" else [args.algorithm]
    args.output_dir.mkdir(parents=True, exist_ok=True)
    args.summary_dir.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, object]] = []

    for algorithm in algorithms:
        for candidate in config["candidates"][algorithm]:
            estimator = make_estimator(
                algorithm, candidate["parameters"], config["selection"]["random_seed"], config["selection"]["thread_limit"],
            )
            model_path = args.output_dir / f"{args.target}_{algorithm}_{candidate['id']}_validation_v01.joblib"
            if args.rescore_only:
                if not model_path.exists():
                    raise FileNotFoundError(f"Saved candidate model not found: {model_path}")
                model = joblib.load(model_path)
            else:
                model = Pipeline([("preprocess", make_preprocessor()), ("model", estimator)])
                model.fit(train[FEATURES], train.label)
            probability = model.predict_proba(validation[FEATURES])[:, 1]
            row = {
                "target": args.target,
                "algorithm": algorithm,
                "candidate_id": candidate["id"],
                "train_rows": len(train),
                "train_events": int(train.label.sum()),
                "validation_rows": len(validation),
                "validation_events": int(validation.label.sum()),
                "parameters_json": json.dumps(candidate["parameters"], sort_keys=True),
                **score(validation.label, probability),
            }
            rows.append(row)
            if not args.rescore_only:
                joblib.dump(model, model_path)
            print(f"{'rescored' if args.rescore_only else 'completed'} {args.target} {algorithm} {candidate['id']}: PR-AUC={row['pr_auc']:.6f}", flush=True)

    candidate_path = args.summary_dir / f"{args.target}_validation_candidates_v01.csv"
    table = pd.DataFrame(rows)
    if candidate_path.exists():
        previous = pd.read_csv(candidate_path)
        previous = previous.loc[~previous.algorithm.isin(algorithms)]
        table = pd.concat([previous, table], ignore_index=True)
    table = table.sort_values(["algorithm", "pr_auc"], ascending=[True, False])
    table.to_csv(candidate_path, index=False)
    selected = table.sort_values(["algorithm", "pr_auc", "roc_auc", "brier_uncalibrated"], ascending=[True, False, False, True]).groupby("algorithm", as_index=False).head(1)
    selected.to_csv(args.summary_dir / f"{args.target}_validation_selection_v01.csv", index=False)
    manifest = {
        "version": "tree_hyperparameter_selection_v01",
        "target": args.target,
        "protocol": "train_and_validation_only",
        "oot_file_opened": False,
        "selection_metric": config["selection"]["primary_metric"],
        "selected": selected.to_dict(orient="records"),
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    (args.summary_dir / f"{args.target}_validation_selection_manifest_v01.json").write_text(json.dumps(manifest, indent=2) + "\n")


if __name__ == "__main__":
    main()
