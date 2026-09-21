#!/usr/bin/env python3
"""Describe Q1/Q3 cohort comparability for the Fannie Mae robustness extension."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import duckdb
import matplotlib.pyplot as plt
import pandas as pd


Q1 = ("2006Q1", "2008Q1", "2012Q1", "2016Q1", "2020Q1", "2022Q1", "2024Q1")
Q3 = ("2006Q3", "2008Q3", "2012Q3", "2014Q3", "2016Q3", "2018Q3", "2020Q3", "2022Q3", "2024Q3")


def sql_paths(paths: list[Path]) -> str:
    return "[" + ", ".join(repr(str(path)) for path in paths) + "]"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--processed-dir", type=Path, default=Path("fannie_mae/data/processed"))
    parser.add_argument("--reports-dir", type=Path, default=Path("fannie_mae/reports/q1_q3_robustness_v01"))
    parser.add_argument("--figures-dir", type=Path, default=Path("fannie_mae/reports/figures/q1_q3_robustness_v01"))
    args = parser.parse_args()
    args.reports_dir.mkdir(parents=True, exist_ok=True)
    args.figures_dir.mkdir(parents=True, exist_ok=True)

    cohorts = Q1 + Q3
    panels = [args.processed_dir / f"{cohort}_monthly_panel_base.parquet" for cohort in cohorts]
    outcomes = [args.processed_dir / f"{cohort}_outcomes_v01.parquet" for cohort in cohorts]
    con = duckdb.connect()
    con.execute("SET threads = 2")
    con.execute(f"CREATE VIEW panel AS SELECT *, regexp_extract(filename, '([0-9]{{4}}Q[1-4])_', 1) AS cohort FROM read_parquet({sql_paths(panels)}, filename=true)")
    con.execute(f"CREATE VIEW outcome AS SELECT *, regexp_extract(filename, '([0-9]{{4}}Q[1-4])_', 1) AS cohort FROM read_parquet({sql_paths(outcomes)}, filename=true)")

    overview = con.execute("""
        WITH first_observation AS (
          SELECT *, row_number() OVER (PARTITION BY cohort, loan_identifier ORDER BY monthly_reporting_period) AS rn
          FROM panel
        ), base AS (
          SELECT cohort, count(*) AS loan_month_rows, count(DISTINCT loan_identifier) AS loans,
            round(avg(CASE WHEN try_cast(current_loan_delinquency_status AS INTEGER) BETWEEN 1 AND 98 THEN 1 ELSE 0 END) * 100, 4) AS current_30plus_dpd_pct,
            round(avg(CASE WHEN try_cast(current_loan_delinquency_status AS INTEGER) BETWEEN 3 AND 98 THEN 1 ELSE 0 END) * 100, 4) AS current_90plus_dpd_pct
          FROM panel GROUP BY 1
        ), origination AS (
          SELECT cohort, round(avg(borrower_credit_score_at_origination), 2) AS mean_fico,
            round(avg(debt_to_income_dti), 2) AS mean_dti,
            round(avg(original_loan_to_value_ratio_ltv), 2) AS mean_ltv,
            round(avg(original_interest_rate), 3) AS mean_original_rate
          FROM first_observation WHERE rn = 1 GROUP BY 1
        ), labels AS (
          SELECT cohort,
            sum(CASE WHEN formal_adverse_6m IS NOT NULL THEN 1 ELSE 0 END) AS formal_eligible,
            round(avg(CASE WHEN formal_adverse_6m = 1 THEN 1 ELSE 0 END) FILTER (WHERE formal_adverse_6m IS NOT NULL) * 100, 4) AS formal_adverse_6m_pct,
            sum(CASE WHEN early_deterioration_6m IS NOT NULL THEN 1 ELSE 0 END) AS early_eligible,
            round(avg(CASE WHEN early_deterioration_6m = 1 THEN 1 ELSE 0 END) FILTER (WHERE early_deterioration_6m IS NOT NULL) * 100, 4) AS early_deterioration_6m_pct
          FROM outcome GROUP BY 1
        )
        SELECT base.*, origination.mean_fico, origination.mean_dti, origination.mean_ltv, origination.mean_original_rate,
          labels.formal_eligible, labels.formal_adverse_6m_pct, labels.early_eligible, labels.early_deterioration_6m_pct,
          substr(base.cohort, 1, 4)::INTEGER AS acquisition_year, substr(base.cohort, 5, 2) AS acquisition_quarter
        FROM base JOIN origination USING (cohort) JOIN labels USING (cohort)
        ORDER BY acquisition_year, acquisition_quarter
    """).fetchdf()
    overview.to_csv(args.reports_dir / "01_q1_q3_cohort_summary.csv", index=False)

    shared = overview[overview.acquisition_year.isin([2006, 2008, 2012, 2016, 2020, 2022, 2024])]
    paired = shared.pivot(index="acquisition_year", columns="acquisition_quarter", values=[
        "formal_adverse_6m_pct", "early_deterioration_6m_pct", "mean_fico", "mean_ltv", "mean_original_rate"
    ])
    paired.columns = [f"{metric}_{quarter}" for metric, quarter in paired.columns]
    paired = paired.reset_index()
    for metric in ("formal_adverse_6m_pct", "early_deterioration_6m_pct", "mean_fico", "mean_ltv", "mean_original_rate"):
        paired[f"{metric}_q3_minus_q1"] = paired[f"{metric}_Q3"] - paired[f"{metric}_Q1"]
    paired.to_csv(args.reports_dir / "02_matched_q1_q3_comparison.csv", index=False)

    plt.style.use("seaborn-v0_8-whitegrid")
    years = paired["acquisition_year"].astype(str)
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.8))
    for ax, metric, title in zip(
        axes,
        ("formal_adverse_6m_pct", "early_deterioration_6m_pct"),
        ("Formal adverse outcome (90+ DPD)", "Early deterioration outcome (30+ DPD)"),
    ):
        ax.plot(years, paired[f"{metric}_Q1"], marker="o", label="Q1")
        ax.plot(years, paired[f"{metric}_Q3"], marker="o", label="Q3")
        ax.set_title(title); ax.set_xlabel("Acquisition year"); ax.set_ylabel("Six-month rate, %"); ax.legend()
    fig.suptitle("Outcome rates by matched Q1 and Q3 acquisition cohorts")
    fig.tight_layout(); fig.savefig(args.figures_dir / "01_q1_q3_outcome_comparison.png", dpi=180); plt.close(fig)

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.8))
    for ax, metric, title, label in zip(
        axes, ("mean_fico", "mean_ltv"), ("Mean origination FICO", "Mean original LTV"), ("FICO", "LTV, %")
    ):
        ax.plot(years, paired[f"{metric}_Q1"], marker="o", label="Q1")
        ax.plot(years, paired[f"{metric}_Q3"], marker="o", label="Q3")
        ax.set_title(title); ax.set_xlabel("Acquisition year"); ax.set_ylabel(label); ax.legend()
    fig.suptitle("Selected origination characteristics by matched Q1 and Q3 cohorts")
    fig.tight_layout(); fig.savefig(args.figures_dir / "02_q1_q3_origination_comparison.png", dpi=180); plt.close(fig)

    metadata = {
        "version": "fannie_q1_q3_robustness_v01",
        "q1_cohorts": list(Q1), "q3_cohorts": list(Q3),
        "unit_of_analysis": "loan-month",
        "interpretation": "Descriptive comparison only. Differences between Q1 and Q3 cohorts may reflect composition, calendar conditions, and origination-quarter effects; they are not causal estimates.",
    }
    (args.reports_dir / "q1_q3_robustness_metadata.json").write_text(json.dumps(metadata, indent=2) + "\n")
    con.close()


if __name__ == "__main__":
    main()
