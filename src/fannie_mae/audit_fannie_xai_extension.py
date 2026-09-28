#!/usr/bin/env python3
"""Run a bounded, reproducible supplementary XAI audit on validation data.

The audit deliberately uses the frozen six-month XGBoost models and the
2017--2020 validation period only.  It does not retrain a model, choose an
alert threshold, or make a further OOT performance claim.  It produces:

* permutation importance for ranking performance;
* ALE profiles for the four most important numeric variables;
* a descriptive comparison of local SHAP factors among policy-capacity alerts
  from stress-issuance and reference-issuance cohorts.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.metrics import average_precision_score, roc_auc_score

from evaluate_fannie_alert_policy import FEATURES


TARGETS = ("formal_adverse_6m", "early_deterioration_6m")
NUMERIC_FEATURES = {
    "original_interest_rate",
    "original_upb",
    "original_loan_term",
    "original_loan_to_value_ratio_ltv",
    "original_combined_loan_to_value_ratio_cltv",
    "number_of_borrowers",
    "debt_to_income_dti",
    "borrower_credit_score_at_origination",
    "co_borrower_credit_score_at_origination",
    "mortgage_insurance_percentage",
    "current_interest_rate",
    "current_actual_upb",
    "loan_age",
    "remaining_months_to_legal_maturity",
    "remaining_months_to_maturity",
    "number_of_units",
}
STRESS_COHORTS = {"2008Q1", "2020Q1"}
REFERENCE_COHORTS = {"2012Q1", "2016Q1"}


def predict_raw(model, frame: pd.DataFrame) -> np.ndarray:
    return model.predict_proba(frame[FEATURES])[:, 1]


def shap_importance(model, frame: pd.DataFrame) -> pd.Series:
    transformed = model.named_steps["preprocess"].transform(frame[FEATURES])
    names = model.named_steps["preprocess"].get_feature_names_out()
    values = model.named_steps["model"].get_booster().predict(
        xgb.DMatrix(transformed, feature_names=list(names)), pred_contribs=True
    )[:, :-1]
    return pd.Series(np.abs(values).mean(axis=0), index=names)


def permutation_importance(model, frame: pd.DataFrame, repeats: int) -> pd.DataFrame:
    y = frame["label"].to_numpy()
    baseline = predict_raw(model, frame)
    baseline_roc = roc_auc_score(y, baseline)
    baseline_pr = average_precision_score(y, baseline)
    rows: list[dict[str, object]] = []
    for feature_index, feature in enumerate(FEATURES):
        roc_drops, pr_drops = [], []
        for repeat in range(repeats):
            shuffled = frame[FEATURES].copy()
            rng = np.random.default_rng(20_260 + feature_index * 100 + repeat)
            shuffled[feature] = rng.permutation(shuffled[feature].to_numpy())
            scores = model.predict_proba(shuffled)[:, 1]
            roc_drops.append(baseline_roc - roc_auc_score(y, scores))
            pr_drops.append(baseline_pr - average_precision_score(y, scores))
        rows.append(
            {
                "feature": feature,
                "baseline_roc_auc": baseline_roc,
                "baseline_pr_auc": baseline_pr,
                "mean_roc_auc_drop": float(np.mean(roc_drops)),
                "std_roc_auc_drop": float(np.std(roc_drops, ddof=0)),
                "mean_pr_auc_drop": float(np.mean(pr_drops)),
                "std_pr_auc_drop": float(np.std(pr_drops, ddof=0)),
                "repeats": repeats,
            }
        )
    result = pd.DataFrame(rows).sort_values("mean_pr_auc_drop", ascending=False)
    result["permutation_rank"] = np.arange(1, len(result) + 1)
    return result


def ale_profile(model, frame: pd.DataFrame, feature: str, bins: int) -> pd.DataFrame:
    values = frame[feature].dropna()
    edges = np.unique(np.quantile(values, np.linspace(0.0, 1.0, bins + 1)))
    if len(edges) < 3:
        return pd.DataFrame()
    contributions: list[float] = []
    counts: list[int] = []
    centers: list[float] = []
    for lower, upper in zip(edges[:-1], edges[1:]):
        if upper == edges[-1]:
            mask = frame[feature].between(lower, upper, inclusive="both")
        else:
            mask = frame[feature].between(lower, upper, inclusive="left")
        group = frame.loc[mask, FEATURES].copy()
        if group.empty:
            continue
        lower_frame, upper_frame = group.copy(), group.copy()
        lower_frame[feature] = lower
        upper_frame[feature] = upper
        contributions.append(float(np.mean(model.predict_proba(upper_frame)[:, 1] - model.predict_proba(lower_frame)[:, 1])))
        counts.append(len(group))
        centers.append(float((lower + upper) / 2))
    if not contributions:
        return pd.DataFrame()
    accumulated = np.cumsum(contributions)
    centered = accumulated - np.average(accumulated, weights=counts)
    return pd.DataFrame(
        {
            "feature": feature,
            "bin_center": centers,
            "local_effect": contributions,
            "ale_centered": centered,
            "bin_observations": counts,
        }
    )


def alert_cohort_shap(
    model, calibrator, frame: pd.DataFrame, target: str, max_alerts_per_group: int
) -> tuple[pd.DataFrame, pd.DataFrame]:
    capacity = 0.01 if target == "formal_adverse_6m" else 0.05
    work = frame.loc[frame.acquisition_cohort.isin(STRESS_COHORTS | REFERENCE_COHORTS)].copy()
    work["cohort_group"] = np.where(
        work.acquisition_cohort.isin(STRESS_COHORTS), "stress_issuance", "reference_issuance"
    )
    work["calibrated_score"] = calibrator.predict(predict_raw(model, work))
    selected: list[pd.DataFrame] = []
    audit_rows: list[dict[str, object]] = []
    for group, group_frame in work.groupby("cohort_group", sort=True):
        ordered = group_frame.sort_values(
            ["calibrated_score", "loan_identifier", "monthly_reporting_period"],
            ascending=[False, True, True],
            kind="mergesort",
        )
        alert_count = max(1, round(len(ordered) * capacity))
        alerts = ordered.iloc[:alert_count]
        if len(alerts) > max_alerts_per_group:
            alerts = alerts.sample(n=max_alerts_per_group, random_state=42)
        selected.append(alerts)
        audit_rows.append(
            {
                "target": target,
                "cohort_group": group,
                "acquisition_cohorts": ", ".join(sorted(STRESS_COHORTS if group == "stress_issuance" else REFERENCE_COHORTS)),
                "validation_rows": len(ordered),
                "alert_capacity_pct": capacity * 100,
                "policy_capacity_alerts": alert_count,
                "alerts_used_for_shap": len(alerts),
                "mean_calibrated_score": float(alerts.calibrated_score.mean()),
            }
        )
    alerts = pd.concat(selected, ignore_index=True)
    transformed = model.named_steps["preprocess"].transform(alerts[FEATURES])
    names = model.named_steps["preprocess"].get_feature_names_out()
    values = model.named_steps["model"].get_booster().predict(
        xgb.DMatrix(transformed, feature_names=list(names)), pred_contribs=True
    )[:, :-1]
    rows: list[dict[str, object]] = []
    for group in ("stress_issuance", "reference_issuance"):
        mask = alerts.cohort_group.eq(group).to_numpy()
        for feature, importance in zip(names, np.abs(values[mask]).mean(axis=0)):
            rows.append({"target": target, "cohort_group": group, "feature": feature, "mean_abs_shap": importance})
    comparison = pd.DataFrame(rows).pivot(index="feature", columns="cohort_group", values="mean_abs_shap").reset_index()
    comparison["feature"] = comparison.feature.str.replace("^(num|cat)__", "", regex=True)
    comparison["stress_rank"] = comparison.stress_issuance.rank(ascending=False, method="min").astype(int)
    comparison["reference_rank"] = comparison.reference_issuance.rank(ascending=False, method="min").astype(int)
    comparison["absolute_rank_change"] = (comparison.stress_rank - comparison.reference_rank).abs()
    correlation = comparison.stress_rank.corr(comparison.reference_rank, method="spearman")
    for row in audit_rows:
        row["spearman_rank_correlation"] = float(correlation)
        row["top_10_overlap"] = int(
            len(
                set(comparison.nsmallest(10, "stress_rank").feature)
                & set(comparison.nsmallest(10, "reference_rank").feature)
            )
        )
    return comparison.sort_values("stress_rank"), pd.DataFrame(audit_rows)


def save_chart(data: pd.DataFrame, target: str, figures_dir: Path) -> None:
    top = data.nsmallest(10, "stress_rank").sort_values("stress_issuance")
    fig, axis = plt.subplots(figsize=(9, 5.5))
    positions = np.arange(len(top))
    height = 0.36
    axis.barh(positions - height / 2, top.reference_issuance, height=height, label="Reference issuance: 2012Q1 + 2016Q1", alpha=0.78, color="#168a9a")
    axis.barh(positions + height / 2, top.stress_issuance, height=height, label="Stress issuance: 2008Q1 + 2020Q1", alpha=0.72, color="#bf6b00")
    axis.set_yticks(positions, top.feature)
    axis.set(xlabel="Mean absolute SHAP value", title=f"Alert explanations by issuance cohort: {target}")
    axis.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(figures_dir / f"{target}_alert_cohort_shap_comparison_v01.png", dpi=180)
    plt.close(fig)


def save_ale_chart(data: pd.DataFrame, target: str, figures_dir: Path) -> None:
    features = list(data.feature.drop_duplicates())
    fig, axes = plt.subplots(2, 2, figsize=(10, 6.5))
    for axis, feature in zip(axes.flat, features):
        part = data.loc[data.feature.eq(feature)]
        axis.plot(part.bin_center, part.ale_centered, marker="o", color="#15375d")
        axis.axhline(0, color="#6d6a68", linewidth=0.8)
        axis.set(title=feature, xlabel="Feature value", ylabel="Centered ALE")
    for axis in axes.flat[len(features):]:
        axis.axis("off")
    fig.suptitle(f"Validation ALE profiles: {target}")
    fig.tight_layout()
    fig.savefig(figures_dir / f"{target}_validation_ale_v01.png", dpi=180)
    plt.close(fig)


def write_alert_audit_summary(reports_dir: Path) -> None:
    """Create the dissertation-ready two-outcome cohort-audit table."""
    frames = []
    for target in TARGETS:
        path = reports_dir / f"{target}_alert_cohort_shap_audit_v01.csv"
        if path.exists():
            frames.append(pd.read_csv(path))
    if len(frames) != len(TARGETS):
        return
    rows: list[dict[str, object]] = []
    for target, group in pd.concat(frames, ignore_index=True).groupby("target", sort=True):
        stress = group.loc[group.cohort_group.eq("stress_issuance")].iloc[0]
        reference = group.loc[group.cohort_group.eq("reference_issuance")].iloc[0]
        rows.append(
            {
                "target": target,
                "stress_issuance_cohorts": stress.acquisition_cohorts,
                "reference_issuance_cohorts": reference.acquisition_cohorts,
                "alert_tier": "Red" if target == "formal_adverse_6m" else "Amber",
                "alert_capacity_pct": stress.alert_capacity_pct,
                "stress_validation_rows": stress.validation_rows,
                "reference_validation_rows": reference.validation_rows,
                "stress_policy_capacity_alerts": stress.policy_capacity_alerts,
                "reference_policy_capacity_alerts": reference.policy_capacity_alerts,
                "stress_alerts_used_for_shap": stress.alerts_used_for_shap,
                "reference_alerts_used_for_shap": reference.alerts_used_for_shap,
                "spearman_rank_correlation": stress.spearman_rank_correlation,
                "top_10_overlap": stress.top_10_overlap,
            }
        )
    pd.DataFrame(rows).to_csv(reports_dir / "xai_alert_cohort_shap_audit_summary_v01.csv", index=False)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", choices=TARGETS, required=True)
    parser.add_argument("--sample-size", type=int, default=30_000)
    parser.add_argument("--permutation-repeats", type=int, default=3)
    parser.add_argument("--ale-bins", type=int, default=10)
    parser.add_argument("--max-alerts-per-group", type=int, default=1_000)
    parser.add_argument("--samples-dir", type=Path, default=Path("fannie_mae/data/model_samples_v01"))
    parser.add_argument("--models-dir", type=Path, default=Path("fannie_mae/models/xgboost_v01"))
    parser.add_argument("--reports-dir", type=Path, default=Path("fannie_mae/reports/xai_extension_v01"))
    parser.add_argument("--figures-dir", type=Path, default=Path("fannie_mae/reports/figures/xai_extension_v01"))
    args = parser.parse_args()
    args.reports_dir.mkdir(parents=True, exist_ok=True)
    args.figures_dir.mkdir(parents=True, exist_ok=True)

    validation = pd.read_parquet(args.samples_dir / f"{args.target}_validation_sample_v01.parquet")
    sample = validation.sample(n=min(args.sample_size, len(validation)), random_state=42).reset_index(drop=True)
    model = joblib.load(args.models_dir / f"{args.target}_xgboost_v01.joblib")
    calibrator = joblib.load(args.models_dir / f"{args.target}_xgboost_isotonic_calibrator_v01.joblib")

    permutation = permutation_importance(model, sample, args.permutation_repeats)
    shap = (
        shap_importance(model, sample)
        .rename("mean_abs_shap")
        .reset_index()
        .rename(columns={"index": "transformed_feature"})
    )
    shap["feature"] = shap.transformed_feature.str.replace("^(num|cat)__", "", regex=True)
    shap = shap.groupby("feature", as_index=False).mean(numeric_only=True)
    combined = permutation.merge(shap, on="feature", how="left")
    combined["shap_rank"] = combined.mean_abs_shap.rank(ascending=False, method="min").astype(int)
    combined["absolute_rank_change"] = (combined.permutation_rank - combined.shap_rank).abs()
    combined = combined.sort_values("permutation_rank")
    combined.to_csv(args.reports_dir / f"{args.target}_validation_permutation_importance_v01.csv", index=False)

    numeric_top = [feature for feature in combined.feature if feature in NUMERIC_FEATURES][:4]
    ale = pd.concat([ale_profile(model, sample, feature, args.ale_bins) for feature in numeric_top], ignore_index=True)
    ale.to_csv(args.reports_dir / f"{args.target}_validation_ale_v01.csv", index=False)
    save_ale_chart(ale, args.target, args.figures_dir)

    alert_comparison, alert_audit = alert_cohort_shap(model, calibrator, validation, args.target, args.max_alerts_per_group)
    alert_comparison.to_csv(args.reports_dir / f"{args.target}_alert_cohort_shap_comparison_v01.csv", index=False)
    alert_audit.to_csv(args.reports_dir / f"{args.target}_alert_cohort_shap_audit_v01.csv", index=False)
    write_alert_audit_summary(args.reports_dir)
    save_chart(alert_comparison, args.target, args.figures_dir)

    summary = {
        "target": args.target,
        "source_period": "validation_2017_01_to_2020_12",
        "validation_rows": int(len(validation)),
        "permutation_sample_rows": int(len(sample)),
        "permutation_repeats": args.permutation_repeats,
        "ale_bins": args.ale_bins,
        "top_numeric_features_for_ale": numeric_top,
        "shap_permutation_spearman_rank_correlation": float(combined.permutation_rank.corr(combined.shap_rank, method="spearman")),
        "cohort_comparison": "stress issuance (2008Q1, 2020Q1) versus reference issuance (2012Q1, 2016Q1)",
        "restriction": "descriptive explanation audit; not a causal crisis-effect estimate and not an OOT model-selection exercise",
    }
    (args.reports_dir / f"{args.target}_xai_extension_manifest_v01.json").write_text(json.dumps(summary, indent=2) + "\n")


if __name__ == "__main__":
    main()
