#!/usr/bin/env python3
"""Evaluate frozen natural-rate XGBoost models once on the Q1 OOT sample.

The script never fits a model or calibrator. Alert capacities are fixed before
the OOT run and treated as a review-budget policy rather than as tuned score
thresholds.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import duckdb
import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.calibration import calibration_curve
from sklearn.metrics import average_precision_score, brier_score_loss, roc_auc_score


NUMERIC = [
    "original_interest_rate", "original_upb", "original_loan_term",
    "original_loan_to_value_ratio_ltv", "original_combined_loan_to_value_ratio_cltv",
    "number_of_borrowers", "debt_to_income_dti", "borrower_credit_score_at_origination",
    "co_borrower_credit_score_at_origination", "mortgage_insurance_percentage",
    "current_interest_rate", "current_actual_upb", "loan_age",
    "remaining_months_to_legal_maturity", "remaining_months_to_maturity",
]
CATEGORICAL = [
    "channel", "first_time_home_buyer_indicator", "loan_purpose", "property_type",
    "number_of_units", "occupancy_status", "property_state", "amortization_type",
    "current_loan_delinquency_status", "modification_flag",
]
FEATURES = NUMERIC + CATEGORICAL
SHARES = (1, 5, 10, 25)
COHORTS = ("2006Q1", "2008Q1", "2012Q1", "2016Q1", "2020Q1", "2022Q1", "2024Q1")
POLICY = {
    "formal_adverse_6m": {"tier": "Red", "capacity": 0.01, "event_condition": "TRY_CAST(p.current_loan_delinquency_status AS INTEGER) BETWEEN 3 AND 98"},
    "early_deterioration_6m": {"tier": "Amber", "capacity": 0.05, "event_condition": "TRY_CAST(p.current_loan_delinquency_status AS INTEGER) BETWEEN 1 AND 98"},
}


def predict(model, calibrator, frame: pd.DataFrame) -> tuple[np.ndarray, np.ndarray]:
    raw_parts, calibrated_parts = [], []
    for start in range(0, len(frame), 100_000):
        raw = model.predict_proba(frame.iloc[start:start + 100_000][FEATURES])[:, 1]
        raw_parts.append(raw)
        calibrated_parts.append(calibrator.predict(raw))
    return np.concatenate(raw_parts), np.concatenate(calibrated_parts)


def lead_time(selected: pd.DataFrame, target: str, processed_dir: Path) -> dict[str, float | int | None]:
    positives = selected.loc[selected.label == 1, ["loan_identifier", "monthly_reporting_period", "acquisition_cohort"]].copy()
    if positives.empty:
        return {"alerted_events_with_observed_event": 0, "mean_lead_time_months": None, "median_lead_time_months": None, "min_lead_time_months": None, "max_lead_time_months": None}
    paths = "[" + ", ".join(repr(str(processed_dir / f"{cohort}_monthly_panel_base.parquet")) for cohort in COHORTS) + "]"
    con = duckdb.connect()
    con.execute("SET threads = 2")
    con.register("selected_positive_alerts", positives)
    query = f"""
        WITH panel AS (
            SELECT *, regexp_extract(filename, '([0-9]{{4}}Q[1-4])_', 1) AS acquisition_cohort
            FROM read_parquet({paths}, filename=true)
        ), hits AS (
            SELECT s.loan_identifier, s.monthly_reporting_period AS alert_month,
              min(date_diff('month', s.monthly_reporting_period, p.monthly_reporting_period)) AS months_to_event
            FROM selected_positive_alerts s
            JOIN panel p USING (acquisition_cohort, loan_identifier)
            WHERE p.monthly_reporting_period > s.monthly_reporting_period
              AND p.monthly_reporting_period <= s.monthly_reporting_period + INTERVAL 6 MONTH
              AND {POLICY[target]['event_condition']}
            GROUP BY 1, 2
        )
        SELECT count(*) AS alerted_events_with_observed_event,
          avg(months_to_event) AS mean_lead_time_months,
          quantile_cont(months_to_event, 0.5) AS median_lead_time_months,
          min(months_to_event) AS min_lead_time_months,
          max(months_to_event) AS max_lead_time_months
        FROM hits
    """
    row = con.execute(query).fetchone()
    con.close()
    return {
        "alerted_events_with_observed_event": int(row[0]),
        "mean_lead_time_months": round(float(row[1]), 6) if row[1] is not None else None,
        "median_lead_time_months": round(float(row[2]), 6) if row[2] is not None else None,
        "min_lead_time_months": int(row[3]) if row[3] is not None else None,
        "max_lead_time_months": int(row[4]) if row[4] is not None else None,
    }


def build_figures(metrics: pd.DataFrame, reliability: pd.DataFrame, target: str, figures_dir: Path) -> None:
    figures_dir.mkdir(parents=True, exist_ok=True)
    ordered = metrics.sort_values("train_share_pct")
    fig, axes = plt.subplots(2, 2, figsize=(11, 7.5))
    plots = [
        ("roc_auc_calibrated", "ROC-AUC"),
        ("pr_auc_calibrated", "PR-AUC"),
        ("brier_calibrated", "Calibrated Brier score"),
        ("mean_lead_time_months", "Mean lead time, months"),
    ]
    for axis, (column, label) in zip(axes.flat, plots):
        axis.plot(ordered.train_share_pct, ordered[column], marker="o", color="#15375d", linewidth=2)
        axis.set(xlabel="Natural training sample, %", ylabel=label)
        axis.set_xticks(list(SHARES))
        axis.grid(alpha=0.25)
    fig.suptitle(f"Training-size sensitivity on fixed OOT sample: {target}")
    fig.tight_layout()
    fig.savefig(figures_dir / f"{target}_train_size_oot_metrics_v01.png", dpi=180)
    plt.close(fig)

    fig, axis = plt.subplots(figsize=(6.8, 5.1))
    for share, group in reliability.groupby("train_share_pct", sort=True):
        axis.plot(group.mean_predicted_probability, group.observed_event_rate, marker="o", label=f"{share}%")
    axis.plot([0, 1], [0, 1], linestyle="--", color="#666666", label="Perfect calibration")
    axis.set(xlabel="Mean calibrated probability", ylabel="Observed event rate", title=f"OOT reliability: {target}")
    axis.legend(title="Train share")
    axis.grid(alpha=0.25)
    fig.tight_layout()
    fig.savefig(figures_dir / f"{target}_train_size_oot_calibration_v01.png", dpi=180)
    plt.close(fig)


def evaluate_target(target: str, args: argparse.Namespace) -> tuple[pd.DataFrame, pd.DataFrame]:
    test_path = args.samples_dir / f"{target}_out_of_time_test_sample_v01.parquet"
    test = pd.read_parquet(test_path)
    if not (test.split == "out_of_time_test").all():
        raise ValueError(f"Unexpected split values in {test_path}")
    policy = POLICY[target]
    rows, reliability_rows = [], []
    for share in SHARES:
        print(f"Scoring {target} at {share}% on fixed OOT sample ({len(test):,} rows)...", flush=True)
        model_dir = args.models_dir / target / f"{share:02d}pct"
        manifest = json.loads((model_dir / "fit_and_calibration_manifest.json").read_text())
        if manifest.get("oot_accessed") is not False:
            raise ValueError(f"Model manifest is not eligible for first OOT evaluation: {model_dir}")
        model = joblib.load(model_dir / "model.joblib")
        calibrator = joblib.load(model_dir / "isotonic_calibrator.joblib")
        raw, calibrated = predict(model, calibrator, test)
        ranked = test[["loan_identifier", "monthly_reporting_period", "acquisition_cohort", "label"]].copy()
        ranked["score"] = calibrated
        ranked = ranked.sort_values(["score", "loan_identifier", "monthly_reporting_period"], ascending=[False, True, True], kind="mergesort")
        alert_count = max(1, round(len(ranked) * policy["capacity"]))
        selected = ranked.iloc[:alert_count].copy()
        tp = int(selected.label.sum())
        total_events = int(test.label.sum())
        lead = lead_time(selected, target, args.processed_dir)
        row = {
            "target": target,
            "tier": policy["tier"],
            "train_share_pct": share,
            "oot_rows": len(test),
            "oot_events": total_events,
            "oot_event_rate_pct": round(float(test.label.mean() * 100), 6),
            "roc_auc_raw": round(float(roc_auc_score(test.label, raw)), 6),
            "pr_auc_raw": round(float(average_precision_score(test.label, raw)), 6),
            "roc_auc_calibrated": round(float(roc_auc_score(test.label, calibrated)), 6),
            "pr_auc_calibrated": round(float(average_precision_score(test.label, calibrated)), 6),
            "brier_calibrated": round(float(brier_score_loss(test.label, calibrated)), 6),
            "alert_capacity_pct": policy["capacity"] * 100,
            "alert_count": alert_count,
            "threshold_score": round(float(selected.score.iloc[-1]), 8),
            "true_positives": tp,
            "false_positives": alert_count - tp,
            "trigger_precision_pct": round(100 * tp / alert_count, 6),
            "trigger_recall_pct": round(100 * tp / total_events, 6),
            "false_alerts_per_true_positive": round((alert_count - tp) / tp, 6) if tp else None,
            **lead,
        }
        rows.append(row)
        observed, predicted = calibration_curve(test.label, calibrated, n_bins=10, strategy="quantile")
        reliability_rows.extend({
            "target": target, "train_share_pct": share, "bin": index + 1,
            "mean_predicted_probability": predicted_value,
            "observed_event_rate": observed_value,
        } for index, (predicted_value, observed_value) in enumerate(zip(predicted, observed)))
    metrics = pd.DataFrame(rows)
    reliability = pd.DataFrame(reliability_rows)
    metrics.to_csv(args.reports_dir / f"{target}_train_size_oot_metrics_v01.csv", index=False)
    reliability.to_csv(args.reports_dir / f"{target}_train_size_oot_calibration_v01.csv", index=False)
    build_figures(metrics, reliability, target, args.figures_dir)
    return metrics, reliability


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--samples-dir", type=Path, default=Path("fannie_mae/data/model_samples_v01"))
    parser.add_argument("--models-dir", type=Path, default=Path("fannie_mae/models/train_size_sensitivity_v01"))
    parser.add_argument("--processed-dir", type=Path, default=Path("fannie_mae/data/processed"))
    parser.add_argument("--reports-dir", type=Path, default=Path("fannie_mae/reports/train_size_sensitivity_v01"))
    parser.add_argument("--figures-dir", type=Path, default=Path("fannie_mae/reports/figures/train_size_sensitivity_v01"))
    args = parser.parse_args()
    args.reports_dir.mkdir(parents=True, exist_ok=True)
    all_metrics = []
    for target in POLICY:
        metrics, _ = evaluate_target(target, args)
        all_metrics.append(metrics)
    combined = pd.concat(all_metrics, ignore_index=True)
    combined.to_csv(args.reports_dir / "train_size_oot_metrics_summary_v01.csv", index=False)
    print("Completed one-time OOT evaluation for all frozen train-size models.", flush=True)


if __name__ == "__main__":
    main()
