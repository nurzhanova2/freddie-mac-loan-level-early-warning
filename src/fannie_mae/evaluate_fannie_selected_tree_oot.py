#!/usr/bin/env python3
"""Calibrate validation-selected tree models and run their one-time OOT test."""
from __future__ import annotations

import argparse
import gc
import json
from datetime import datetime, timezone
from pathlib import Path

import duckdb
import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yaml
from sklearn.calibration import calibration_curve
from sklearn.isotonic import IsotonicRegression
from sklearn.metrics import average_precision_score, brier_score_loss, roc_auc_score


FEATURES = [
    "original_interest_rate", "original_upb", "original_loan_term", "original_loan_to_value_ratio_ltv",
    "original_combined_loan_to_value_ratio_cltv", "number_of_borrowers", "debt_to_income_dti",
    "borrower_credit_score_at_origination", "co_borrower_credit_score_at_origination",
    "mortgage_insurance_percentage", "current_interest_rate", "current_actual_upb", "loan_age",
    "remaining_months_to_legal_maturity", "remaining_months_to_maturity", "channel",
    "first_time_home_buyer_indicator", "loan_purpose", "property_type", "number_of_units",
    "occupancy_status", "property_state", "amortization_type", "current_loan_delinquency_status", "modification_flag",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=Path("fannie_mae/config/fannie_tree_oot_evaluation_v01.yml"))
    parser.add_argument("--models-dir", type=Path, default=Path("fannie_mae/models/tuned_trees_validation_v01"))
    parser.add_argument("--processed-dir", type=Path, default=Path("fannie_mae/data/processed"))
    parser.add_argument("--reports-dir", type=Path, default=Path("fannie_mae/reports/tree_hyperparameter_selection_v01"))
    parser.add_argument("--figures-dir", type=Path, default=Path("fannie_mae/reports/figures/tree_hyperparameter_selection_v01"))
    parser.add_argument("--target", choices=["formal_adverse_6m", "early_deterioration_6m"])
    return parser.parse_args()


def chunked_predict(model, frame: pd.DataFrame) -> np.ndarray:
    return np.concatenate([
        model.predict_proba(frame.iloc[start:start + 100_000][FEATURES])[:, 1]
        for start in range(0, len(frame), 100_000)
    ])


def metrics(y: pd.Series, raw: np.ndarray, calibrated: np.ndarray) -> dict[str, float]:
    return {
        "roc_auc_raw": float(roc_auc_score(y, raw)),
        "pr_auc_raw": float(average_precision_score(y, raw)),
        "roc_auc_calibrated": float(roc_auc_score(y, calibrated)),
        "pr_auc_calibrated": float(average_precision_score(y, calibrated)),
        "brier_raw": float(brier_score_loss(y, raw)),
        "brier_calibrated": float(brier_score_loss(y, calibrated)),
    }


def model_specs(config: dict[str, object], target: str) -> list[dict[str, str]]:
    current = config["comparators"][target]
    candidates = [current["selected_candidate"], *current["fixed_baselines"]]
    unique: dict[tuple[str, str], dict[str, str]] = {}
    for item in candidates:
        unique[(item["algorithm"], item["candidate_id"])] = item
    return list(unique.values())


def lead_time(selected: pd.DataFrame, target: str, processed_dir: Path) -> pd.DataFrame:
    positives = selected.loc[selected.label == 1, [
        "model_key", "loan_identifier", "monthly_reporting_period", "acquisition_cohort",
    ]].copy()
    if positives.empty:
        return pd.DataFrame(columns=["model_key", "alerted_events_with_observed_event", "mean_lead_time_months", "median_lead_time_months"])
    panel_paths = sorted(processed_dir.glob("*_monthly_panel_base.parquet"))
    if not panel_paths:
        raise FileNotFoundError(f"No monthly panels found in {processed_dir}")
    paths = "[" + ", ".join(repr(str(path)) for path in panel_paths) + "]"
    condition = (
        "TRY_CAST(p.current_loan_delinquency_status AS INTEGER) BETWEEN 3 AND 98"
        if target.startswith("formal_adverse")
        else "TRY_CAST(p.current_loan_delinquency_status AS INTEGER) BETWEEN 1 AND 98"
    )
    con = duckdb.connect()
    con.execute("SET threads = 2")
    con.register("selected_positive_alerts", positives)
    result = con.execute(f"""
        WITH panel AS (
            SELECT *, regexp_extract(filename, '([0-9]{{4}}Q[1-4])_', 1) AS acquisition_cohort
            FROM read_parquet({paths}, filename=true)
        ), hits AS (
            SELECT s.model_key, s.loan_identifier, s.monthly_reporting_period AS alert_month,
              min(date_diff('month', s.monthly_reporting_period, p.monthly_reporting_period)) AS months_to_event
            FROM selected_positive_alerts s
            JOIN panel p USING (acquisition_cohort, loan_identifier)
            WHERE p.monthly_reporting_period > s.monthly_reporting_period
              AND p.monthly_reporting_period <= s.monthly_reporting_period + INTERVAL 6 MONTH
              AND {condition}
            GROUP BY 1, 2, 3
        )
        SELECT model_key, count(*) AS alerted_events_with_observed_event,
          avg(months_to_event) AS mean_lead_time_months,
          quantile_cont(months_to_event, 0.5) AS median_lead_time_months
        FROM hits GROUP BY 1
    """).fetchdf()
    con.close()
    return result


def plot_reliability(curves: list[dict[str, object]], target: str, output: Path) -> None:
    figure, axis = plt.subplots(figsize=(6.5, 5.5))
    for curve in curves:
        axis.plot(curve["predicted"], curve["observed"], marker="o", label=curve["model_key"])
    axis.plot([0, 1], [0, 1], "k--", linewidth=1, label="perfect calibration")
    axis.set(xlabel="Mean predicted probability", ylabel="Observed event rate", title=f"OOT reliability: {target}")
    axis.legend(fontsize=8)
    axis.grid(alpha=0.25)
    figure.tight_layout()
    figure.savefig(output, dpi=180)
    plt.close(figure)


def main() -> None:
    args = parse_args()
    config = yaml.safe_load(args.config.read_text())
    manifest_path = args.reports_dir / "tree_oot_evaluation_manifest_v01.json"
    if manifest_path.exists():
        raise RuntimeError("OOT evaluation has already been recorded; refusing a second run.")
    args.reports_dir.mkdir(parents=True, exist_ok=True)
    args.figures_dir.mkdir(parents=True, exist_ok=True)
    samples_dir = Path(config["data"]["samples_dir"])
    metric_rows: list[dict[str, object]] = []
    alert_frames: list[pd.DataFrame] = []
    calibration_rows: list[dict[str, object]] = []
    progress_path = args.reports_dir / "tree_oot_evaluation_progress_v01.json"
    progress = (
        json.loads(progress_path.read_text()) if progress_path.exists()
        else {"version": "tree_oot_evaluation_v01", "completed_targets": []}
    )

    targets = [args.target] if args.target else list(config["comparators"])
    for target in targets:
        validation = pd.read_parquet(samples_dir / f"{target}_validation_sample_v01.parquet")
        oot = pd.read_parquet(samples_dir / f"{target}_out_of_time_test_sample_v01.parquet")
        if not (validation.split == "validation").all() or not (oot.split == "out_of_time_test").all():
            raise ValueError(f"Unexpected temporal split for {target}")
        policy = config["alert_policy"][target]
        fraction = float(policy["capacity_percent"]) / 100
        curves: list[dict[str, object]] = []
        selected_for_target: list[pd.DataFrame] = []
        for spec in model_specs(config, target):
            algorithm, candidate_id = spec["algorithm"], spec["candidate_id"]
            model_key = f"{algorithm}_{candidate_id}"
            print(f"Scoring {target}: {model_key}", flush=True)
            model_path = args.models_dir / f"{target}_{algorithm}_{candidate_id}_validation_v01.joblib"
            model = joblib.load(model_path)
            validation_raw = chunked_predict(model, validation)
            calibrator = IsotonicRegression(out_of_bounds="clip").fit(validation_raw, validation.label)
            joblib.dump(calibrator, args.models_dir / f"{target}_{algorithm}_{candidate_id}_isotonic_calibrator_v01.joblib")
            oot_raw = chunked_predict(model, oot)
            oot_calibrated = calibrator.predict(oot_raw)
            ranked = oot[["loan_identifier", "monthly_reporting_period", "acquisition_cohort", "label"]].copy()
            ranked["score"] = oot_calibrated
            ranked["model_key"] = model_key
            ranked = ranked.sort_values(["score", "loan_identifier", "monthly_reporting_period"], ascending=[False, True, True], kind="mergesort")
            alert_count = max(1, round(len(ranked) * fraction))
            selected = ranked.iloc[:alert_count].copy()
            tp = int(selected.label.sum())
            total_events = int(oot.label.sum())
            selected_for_target.append(selected)
            observed, predicted = calibration_curve(oot.label, oot_calibrated, n_bins=10, strategy="quantile")
            curves.append({"model_key": model_key, "observed": observed, "predicted": predicted})
            calibration_rows.extend({
                "target": target, "model_key": model_key, "bin": index + 1,
                "mean_predicted_probability": mean_predicted, "observed_event_rate": observed_rate,
            } for index, (mean_predicted, observed_rate) in enumerate(zip(predicted, observed)))
            metric_rows.append({
                "target": target, "model_key": model_key, "algorithm": algorithm, "candidate_id": candidate_id,
                "selection_role": "selected_candidate" if spec == config["comparators"][target]["selected_candidate"] else "fixed_baseline",
                "oot_rows": len(oot), "oot_events": total_events,
                "oot_event_rate_pct": float(oot.label.mean() * 100), **metrics(oot.label, oot_raw, oot_calibrated),
                "tier": policy["tier"], "alert_capacity_pct": float(policy["capacity_percent"]), "alert_count": alert_count,
                "trigger_threshold": float(selected.score.iloc[-1]),
                "trigger_precision_pct": 100 * tp / alert_count,
                "trigger_recall_pct": 100 * tp / total_events,
            })
            del model, validation_raw, calibrator, oot_raw, oot_calibrated, ranked, selected
            gc.collect()
        print(f"Calculating lead time: {target}", flush=True)
        lead = lead_time(pd.concat(selected_for_target, ignore_index=True), target, args.processed_dir)
        target_metrics = pd.DataFrame(metric_rows).loc[lambda x: x.target == target]
        target_metrics = target_metrics.merge(lead, on="model_key", how="left")
        for index, row in target_metrics.iterrows():
            metric_rows[index].update({
                "alerted_events_with_observed_event": int(row.alerted_events_with_observed_event) if pd.notna(row.alerted_events_with_observed_event) else 0,
                "mean_lead_time_months": float(row.mean_lead_time_months) if pd.notna(row.mean_lead_time_months) else None,
                "median_lead_time_months": float(row.median_lead_time_months) if pd.notna(row.median_lead_time_months) else None,
            })
        plot_reliability(curves, target, args.figures_dir / f"{target}_oot_reliability_v01.png")
        alert_frames.extend(selected_for_target)
        target_metrics.to_csv(args.reports_dir / f"{target}_oot_calibrated_comparison_v01.csv", index=False)
        pd.DataFrame([row for row in calibration_rows if row["target"] == target]).to_csv(
            args.reports_dir / f"{target}_oot_reliability_bins_v01.csv", index=False
        )
        pd.concat(selected_for_target, ignore_index=True).to_parquet(
            args.reports_dir / f"{target}_oot_selected_alerts_v01.parquet", index=False
        )
        if target not in progress["completed_targets"]:
            progress["completed_targets"].append(target)
        progress["updated_at_utc"] = datetime.now(timezone.utc).isoformat()
        progress_path.write_text(json.dumps(progress, indent=2) + "\n")
        print(f"Completed OOT checkpoint for {target}.", flush=True)
        del validation, oot, curves, selected_for_target, lead, target_metrics
        gc.collect()

    completed_paths = [
        args.reports_dir / f"{target}_oot_calibrated_comparison_v01.csv"
        for target in config["comparators"]
    ]
    if not all(path.exists() for path in completed_paths):
        print("Saved target checkpoint; awaiting remaining OOT target.", flush=True)
        return
    metrics_table = pd.concat([pd.read_csv(path) for path in completed_paths], ignore_index=True)
    metrics_table = metrics_table.sort_values(["target", "selection_role", "model_key"])
    metrics_table.to_csv(args.reports_dir / "tree_oot_calibrated_comparison_v01.csv", index=False)
    reliability_paths = [
        args.reports_dir / f"{target}_oot_reliability_bins_v01.csv"
        for target in config["comparators"]
    ]
    pd.concat([pd.read_csv(path) for path in reliability_paths], ignore_index=True).to_csv(
        args.reports_dir / "tree_oot_reliability_bins_v01.csv", index=False
    )
    alert_paths = [args.reports_dir / f"{target}_oot_selected_alerts_v01.parquet" for target in config["comparators"]]
    pd.concat([pd.read_parquet(path) for path in alert_paths], ignore_index=True).to_parquet(
        args.reports_dir / "tree_oot_selected_alerts_v01.parquet", index=False
    )
    manifest_path.write_text(json.dumps({
        "version": "tree_oot_evaluation_v01", "oot_accessed": True,
        "calibration_split": "validation_only", "oot_period": config["data"]["out_of_time_test"],
        "model_count": int(len(metrics_table)), "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "metrics_artifact": str(args.reports_dir / "tree_oot_calibrated_comparison_v01.csv"),
    }, indent=2) + "\n")
    print("Completed one-time calibrated OOT evaluation.", flush=True)


if __name__ == "__main__":
    main()
