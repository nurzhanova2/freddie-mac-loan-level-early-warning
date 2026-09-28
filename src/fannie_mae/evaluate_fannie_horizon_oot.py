#!/usr/bin/env python3
"""One-time common-OOT comparison of frozen 3/6/12-month XGBoost models."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import duckdb
import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import average_precision_score, brier_score_loss, roc_auc_score


TARGETS = (
    "formal_adverse_3m", "formal_adverse_6m", "formal_adverse_12m",
    "early_deterioration_3m", "early_deterioration_6m", "early_deterioration_12m",
)
NUMERIC = ["original_interest_rate", "original_upb", "original_loan_term", "original_loan_to_value_ratio_ltv", "original_combined_loan_to_value_ratio_cltv", "number_of_borrowers", "debt_to_income_dti", "borrower_credit_score_at_origination", "co_borrower_credit_score_at_origination", "mortgage_insurance_percentage", "current_interest_rate", "current_actual_upb", "loan_age", "remaining_months_to_legal_maturity", "remaining_months_to_maturity"]
CATEGORICAL = ["channel", "first_time_home_buyer_indicator", "loan_purpose", "property_type", "number_of_units", "occupancy_status", "property_state", "amortization_type", "current_loan_delinquency_status", "modification_flag"]
FEATURES = NUMERIC + CATEGORICAL
COHORTS = ("2006Q1", "2008Q1", "2012Q1", "2016Q1", "2020Q1", "2022Q1", "2024Q1")


def horizon(target: str) -> int:
    return int(target.rsplit("_", 1)[1][:-1])


def family(target: str) -> str:
    return "formal_adverse" if target.startswith("formal_adverse") else "early_deterioration"


def capacity(target: str) -> tuple[str, float]:
    return ("Red", 0.01) if family(target) == "formal_adverse" else ("Amber", 0.05)


def predict(model, calibrator, frame: pd.DataFrame) -> tuple[np.ndarray, np.ndarray]:
    raw_parts, calibrated_parts = [], []
    for start in range(0, len(frame), 100_000):
        raw = model.predict_proba(frame.iloc[start:start + 100_000][FEATURES])[:, 1]
        raw_parts.append(raw)
        calibrated_parts.append(calibrator.predict(raw))
    return np.concatenate(raw_parts), np.concatenate(calibrated_parts)


def observed_lead_time(selected: pd.DataFrame, target: str, processed_dir: Path) -> dict[str, float | int | None]:
    positives = selected.loc[selected.label == 1, ["loan_identifier", "monthly_reporting_period", "acquisition_cohort"]].copy()
    if positives.empty:
        return {"alerted_events_with_observed_event": 0, "mean_lead_time_months": None, "median_lead_time_months": None}
    paths = "[" + ", ".join(repr(str(processed_dir / f"{cohort}_monthly_panel_base.parquet")) for cohort in COHORTS) + "]"
    condition = "TRY_CAST(p.current_loan_delinquency_status AS INTEGER) BETWEEN 3 AND 98" if family(target) == "formal_adverse" else "TRY_CAST(p.current_loan_delinquency_status AS INTEGER) BETWEEN 1 AND 98"
    con = duckdb.connect()
    con.execute("SET threads = 2")
    con.register("selected_positive_alerts", positives)
    row = con.execute(f"""
        WITH panel AS (
            SELECT *, regexp_extract(filename, '([0-9]{{4}}Q[1-4])_', 1) AS acquisition_cohort
            FROM read_parquet({paths}, filename=true)
        ), hits AS (
            SELECT s.loan_identifier, s.monthly_reporting_period AS alert_month,
              min(date_diff('month', s.monthly_reporting_period, p.monthly_reporting_period)) AS months_to_event
            FROM selected_positive_alerts s JOIN panel p USING (acquisition_cohort, loan_identifier)
            WHERE p.monthly_reporting_period > s.monthly_reporting_period
              AND p.monthly_reporting_period <= s.monthly_reporting_period + INTERVAL {horizon(target)} MONTH
              AND {condition}
            GROUP BY 1, 2
        )
        SELECT count(*), avg(months_to_event), quantile_cont(months_to_event, 0.5) FROM hits
    """).fetchone()
    con.close()
    return {
        "alerted_events_with_observed_event": int(row[0]),
        "mean_lead_time_months": round(float(row[1]), 6) if row[1] is not None else None,
        "median_lead_time_months": round(float(row[2]), 6) if row[2] is not None else None,
    }


def figures(metrics: pd.DataFrame, reports: Path, figures_dir: Path) -> None:
    figures_dir.mkdir(parents=True, exist_ok=True)
    for target_family, group in metrics.groupby("outcome_family", sort=True):
        group = group.sort_values("horizon_months")
        fig, axes = plt.subplots(2, 2, figsize=(11, 7.5))
        for axis, (column, label) in zip(axes.flat, [
            ("roc_auc_raw", "ROC-AUC (raw)"), ("pr_auc_raw", "PR-AUC (raw)"),
            ("brier_calibrated", "Calibrated Brier score"), ("mean_lead_time_months", "Mean lead time, months"),
        ]):
            axis.plot(group.horizon_months, group[column], marker="o", linewidth=2, color="#15375d")
            axis.set(xlabel="Prediction horizon, months", ylabel=label)
            axis.set_xticks([3, 6, 12])
            axis.grid(alpha=0.25)
        fig.suptitle(f"Common-OOT horizon comparison: {target_family}")
        fig.tight_layout()
        fig.savefig(figures_dir / f"{target_family}_horizon_oot_metrics_v01.png", dpi=180)
        plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--samples-dir", type=Path, default=Path("fannie_mae/data/horizon_sensitivity_v01"))
    parser.add_argument("--models-dir", type=Path, default=Path("fannie_mae/models/horizon_sensitivity_v01"))
    parser.add_argument("--processed-dir", type=Path, default=Path("fannie_mae/data/processed"))
    parser.add_argument("--reports-dir", type=Path, default=Path("fannie_mae/reports/horizon_sensitivity_v01"))
    parser.add_argument("--figures-dir", type=Path, default=Path("fannie_mae/reports/figures/horizon_sensitivity_v01"))
    args = parser.parse_args()
    args.reports_dir.mkdir(parents=True, exist_ok=True)
    rows = []
    for target in TARGETS:
        test = pd.read_parquet(args.samples_dir / f"{target}_out_of_time_test_sample_v01.parquet")
        if not (test.split == "out_of_time_test").all():
            raise ValueError(f"Unexpected split in OOT sample for {target}")
        model_dir = args.models_dir / target
        manifest = json.loads((model_dir / "fit_and_calibration_manifest.json").read_text())
        if manifest.get("oot_accessed") is not False:
            raise ValueError(f"OOT has already been accessed for {target}")
        print(f"Scoring {target} on common OOT ({len(test):,} rows)...", flush=True)
        model = joblib.load(model_dir / "model.joblib")
        calibrator = joblib.load(model_dir / "isotonic_calibrator.joblib")
        raw, calibrated = predict(model, calibrator, test)
        tier, fraction = capacity(target)
        ranked = test[["loan_identifier", "monthly_reporting_period", "acquisition_cohort", "label"]].copy()
        ranked["score"] = calibrated
        ranked = ranked.sort_values(["score", "loan_identifier", "monthly_reporting_period"], ascending=[False, True, True], kind="mergesort")
        alert_count = max(1, round(len(ranked) * fraction))
        selected = ranked.iloc[:alert_count]
        tp, total_events = int(selected.label.sum()), int(test.label.sum())
        lead = observed_lead_time(selected, target, args.processed_dir)
        rows.append({
            "target": target, "outcome_family": family(target), "horizon_months": horizon(target),
            "tier_for_comparison": tier, "oot_rows": len(test), "oot_events": total_events,
            "oot_event_rate_pct": round(float(test.label.mean() * 100), 6),
            "roc_auc_raw": round(float(roc_auc_score(test.label, raw)), 6),
            "pr_auc_raw": round(float(average_precision_score(test.label, raw)), 6),
            "roc_auc_calibrated": round(float(roc_auc_score(test.label, calibrated)), 6),
            "pr_auc_calibrated": round(float(average_precision_score(test.label, calibrated)), 6),
            "brier_calibrated": round(float(brier_score_loss(test.label, calibrated)), 6),
            "alert_capacity_pct": fraction * 100, "alert_count": alert_count,
            "trigger_precision_pct": round(100 * tp / alert_count, 6),
            "trigger_recall_pct": round(100 * tp / total_events, 6),
            **lead,
        })
    metrics = pd.DataFrame(rows).sort_values(["outcome_family", "horizon_months"])
    metrics.to_csv(args.reports_dir / "horizon_oot_metrics_summary_v01.csv", index=False)
    figures(metrics, args.reports_dir, args.figures_dir)
    for target in TARGETS:
        manifest_path = args.models_dir / target / "fit_and_calibration_manifest.json"
        manifest = json.loads(manifest_path.read_text())
        manifest["oot_accessed"] = True
        manifest["oot_evaluation_artifact"] = str(args.reports_dir / "horizon_oot_metrics_summary_v01.csv")
        manifest_path.write_text(json.dumps(manifest, indent=2, default=str) + "\n")
    print("Completed one-time common-OOT horizon evaluation.", flush=True)


if __name__ == "__main__":
    main()
