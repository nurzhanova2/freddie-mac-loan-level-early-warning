#!/usr/bin/env python3
"""Produce reproducible descriptive tables and figures for Fannie Mae stage 11.

The script reads processed panels only.  It never alters raw archives or
co-mingles Fannie Mae with Freddie Mac data.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import duckdb
import matplotlib.pyplot as plt
import pandas as pd


COHORTS = ("2006Q1", "2008Q1", "2012Q1", "2016Q1", "2020Q1", "2022Q1", "2024Q1")


def query(con: duckdb.DuckDBPyConnection, sql: str) -> pd.DataFrame:
    return con.execute(sql).fetchdf()


def save_csv(frame: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(path, index=False)


def status_band_sql(field: str = "current_loan_delinquency_status") -> str:
    return f"""
        CASE
          WHEN {field} = '00' THEN '00: current'
          WHEN {field} = '01' THEN '01: 30 DPD'
          WHEN {field} = '02' THEN '02: 60 DPD'
          WHEN try_cast({field} AS INTEGER) BETWEEN 3 AND 98 THEN '03+: 90+ DPD'
          WHEN {field} = '99' THEN '99: other/unknown'
          WHEN {field} = 'XX' THEN 'XX: unknown'
          WHEN {field} IS NULL THEN 'missing'
          ELSE 'other'
        END
    """


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--processed-dir", type=Path, default=Path("fannie_mae/data/processed"))
    parser.add_argument("--reports-dir", type=Path, default=Path("fannie_mae/reports/eda_v01"))
    parser.add_argument("--figures-dir", type=Path, default=Path("fannie_mae/reports/figures/eda_v01"))
    args = parser.parse_args()
    args.reports_dir.mkdir(parents=True, exist_ok=True)
    args.figures_dir.mkdir(parents=True, exist_ok=True)

    panel_files = [str(args.processed_dir / f"{c}_monthly_panel_base.parquet") for c in COHORTS]
    outcome_files = [str(args.processed_dir / f"{c}_outcomes_v01.parquet") for c in COHORTS]
    panel_sql_files = "[" + ", ".join(repr(p) for p in panel_files) + "]"
    outcome_sql_files = "[" + ", ".join(repr(p) for p in outcome_files) + "]"
    con = duckdb.connect()
    con.execute("PRAGMA threads=4")
    con.execute(f"CREATE VIEW panel AS SELECT *, regexp_extract(filename, '([0-9]{{4}}Q[1-4])_', 1) AS acquisition_cohort FROM read_parquet({panel_sql_files}, filename=true)")
    con.execute(f"CREATE VIEW outcomes AS SELECT *, regexp_extract(filename, '([0-9]{{4}}Q[1-4])_', 1) AS acquisition_cohort FROM read_parquet({outcome_sql_files}, filename=true)")

    overview = query(con, """
        SELECT acquisition_cohort,
               count(*) AS loan_month_rows,
               count(DISTINCT loan_identifier) AS distinct_loans,
               min(monthly_reporting_period)::DATE AS first_reporting_month,
               max(monthly_reporting_period)::DATE AS last_reporting_month,
               round(avg(loan_age), 2) AS mean_loan_age_months
        FROM panel GROUP BY 1 ORDER BY 1
    """)
    save_csv(overview, args.reports_dir / "01_cohort_overview.csv")

    missingness = query(con, """
        SELECT acquisition_cohort, count(*) AS loan_month_rows,
          round(100.0 * avg(CASE WHEN borrower_credit_score_at_origination IS NULL THEN 1 ELSE 0 END), 3) AS credit_score_missing_pct,
          round(100.0 * avg(CASE WHEN debt_to_income_dti IS NULL THEN 1 ELSE 0 END), 3) AS dti_missing_pct,
          round(100.0 * avg(CASE WHEN original_loan_to_value_ratio_ltv IS NULL THEN 1 ELSE 0 END), 3) AS ltv_missing_pct,
          round(100.0 * avg(CASE WHEN current_actual_upb IS NULL THEN 1 ELSE 0 END), 3) AS current_upb_missing_pct,
          round(100.0 * avg(CASE WHEN current_loan_delinquency_status IS NULL THEN 1 ELSE 0 END), 3) AS delinquency_status_missing_pct,
          round(100.0 * avg(CASE WHEN loan_payment_history IS NULL THEN 1 ELSE 0 END), 3) AS payment_history_missing_pct,
          round(100.0 * avg(CASE WHEN property_state IS NULL THEN 1 ELSE 0 END), 3) AS state_missing_pct
        FROM panel GROUP BY 1 ORDER BY 1
    """)
    save_csv(missingness, args.reports_dir / "02_selected_field_missingness.csv")

    origination = query(con, """
        WITH first_observation AS (
          SELECT *, row_number() OVER (PARTITION BY acquisition_cohort, loan_identifier ORDER BY monthly_reporting_period) AS rn
          FROM panel
        )
        SELECT acquisition_cohort, count(*) AS loans,
          round(avg(borrower_credit_score_at_origination), 1) AS mean_credit_score,
          round(quantile_cont(borrower_credit_score_at_origination, 0.5), 1) AS median_credit_score,
          round(avg(debt_to_income_dti), 2) AS mean_dti,
          round(avg(original_loan_to_value_ratio_ltv), 2) AS mean_ltv,
          round(avg(original_upb), 0) AS mean_original_upb,
          round(100.0 * avg(CASE WHEN first_time_home_buyer_indicator = 'Y' THEN 1 ELSE 0 END), 2) AS first_time_homebuyer_pct
        FROM first_observation WHERE rn = 1 GROUP BY 1 ORDER BY 1
    """)
    save_csv(origination, args.reports_dir / "03_origination_characteristics.csv")

    delinquency = query(con, f"""
        SELECT acquisition_cohort, {status_band_sql()} AS delinquency_band,
               count(*) AS loan_month_rows,
               round(100.0 * count(*) / sum(count(*)) OVER (PARTITION BY acquisition_cohort), 4) AS share_pct
        FROM panel GROUP BY 1, 2 ORDER BY 1, 2
    """)
    save_csv(delinquency, args.reports_dir / "04_current_delinquency_distribution.csv")

    outcomes = query(con, """
        SELECT acquisition_cohort,
          count(*) AS loan_month_rows,
          sum(CASE WHEN formal_adverse_6m IS NOT NULL THEN 1 ELSE 0 END) AS formal_6m_eligible_rows,
          round(100.0 * avg(CASE WHEN formal_adverse_6m = 1 THEN 1 ELSE 0 END) FILTER (WHERE formal_adverse_6m IS NOT NULL), 4) AS formal_adverse_6m_rate_pct,
          sum(CASE WHEN early_deterioration_6m IS NOT NULL THEN 1 ELSE 0 END) AS early_6m_eligible_rows,
          round(100.0 * avg(CASE WHEN early_deterioration_6m = 1 THEN 1 ELSE 0 END) FILTER (WHERE early_deterioration_6m IS NOT NULL), 4) AS early_deterioration_6m_rate_pct,
          round(100.0 * avg(CASE WHEN formal_adverse_6m_status = 'censored' THEN 1 ELSE 0 END), 4) AS formal_6m_censored_share_pct,
          round(100.0 * avg(CASE WHEN early_deterioration_6m_status = 'censored' THEN 1 ELSE 0 END), 4) AS early_6m_censored_share_pct
        FROM outcomes GROUP BY 1 ORDER BY 1
    """)
    save_csv(outcomes, args.reports_dir / "05_six_month_outcome_summary.csv")

    monthly = query(con, f"""
        SELECT monthly_reporting_period::DATE AS reporting_month,
          count(*) AS loan_month_rows,
          round(100.0 * avg(CASE WHEN try_cast(current_loan_delinquency_status AS INTEGER) BETWEEN 1 AND 98 THEN 1 ELSE 0 END), 4) AS dpd_30plus_pct,
          round(100.0 * avg(CASE WHEN try_cast(current_loan_delinquency_status AS INTEGER) BETWEEN 3 AND 98 THEN 1 ELSE 0 END), 4) AS dpd_90plus_pct
        FROM panel GROUP BY 1 ORDER BY 1
    """)
    save_csv(monthly, args.reports_dir / "06_calendar_month_delinquency_trend.csv")

    plt.style.use("seaborn-v0_8-whitegrid")
    fig, ax = plt.subplots(figsize=(10, 5))
    x = range(len(outcomes))
    ax.bar([i - 0.18 for i in x], outcomes["formal_adverse_6m_rate_pct"], 0.36, label="Formal adverse (90+ DPD)")
    ax.bar([i + 0.18 for i in x], outcomes["early_deterioration_6m_rate_pct"], 0.36, label="Early deterioration (30+ DPD)")
    ax.set_xticks(list(x), outcomes["acquisition_cohort"])
    ax.set_ylabel("Rate among eligible observations, %")
    ax.set_title("Six-month labelled outcome rates by acquisition cohort")
    ax.legend()
    fig.tight_layout(); fig.savefig(args.figures_dir / "01_six_month_outcome_rates_by_cohort.png", dpi=180); plt.close(fig)

    pivot = delinquency.pivot(index="acquisition_cohort", columns="delinquency_band", values="share_pct").fillna(0)
    preferred = [c for c in ["00: current", "01: 30 DPD", "02: 60 DPD", "03+: 90+ DPD", "99: other/unknown", "XX: unknown", "missing", "other"] if c in pivot]
    fig, ax = plt.subplots(figsize=(11, 6))
    bottom = pd.Series(0.0, index=pivot.index)
    for col in preferred:
        ax.bar(pivot.index, pivot[col], bottom=bottom, label=col)
        bottom += pivot[col]
    ax.set_ylabel("Share of loan-month rows, %")
    ax.set_title("Observed current delinquency status by acquisition cohort")
    ax.legend(ncol=2, fontsize=8, loc="upper center", bbox_to_anchor=(0.5, -0.14))
    fig.tight_layout(); fig.savefig(args.figures_dir / "02_current_delinquency_distribution.png", dpi=180); plt.close(fig)

    fig, ax = plt.subplots(figsize=(10, 5))
    ax2 = ax.twinx()
    first = ax.plot(origination["acquisition_cohort"], origination["mean_credit_score"], marker="o", color="#1f77b4", label="Mean credit score")
    second = ax2.plot(origination["acquisition_cohort"], origination["mean_ltv"], marker="o", color="#ff7f0e", label="Mean original LTV")
    ax.set_title("Selected origination characteristics by acquisition cohort")
    ax.set_ylabel("Mean credit score")
    ax2.set_ylabel("Mean original LTV, %")
    ax.legend(first + second, [x.get_label() for x in first + second], loc="best")
    fig.tight_layout(); fig.savefig(args.figures_dir / "03_origination_characteristics_trend.png", dpi=180); plt.close(fig)

    miss_long = missingness.melt(id_vars="acquisition_cohort", value_vars=[c for c in missingness if c.endswith("_missing_pct")], var_name="field", value_name="missing_pct")
    fig, ax = plt.subplots(figsize=(11, 5))
    for field, group in miss_long.groupby("field"):
        ax.plot(group["acquisition_cohort"], group["missing_pct"], marker="o", label=field.replace("_missing_pct", ""))
    ax.set_title("Missingness in selected candidate fields")
    ax.set_ylabel("Missing values, % of loan-month rows")
    ax.legend(ncol=2, fontsize=8)
    fig.tight_layout(); fig.savefig(args.figures_dir / "04_selected_field_missingness.png", dpi=180); plt.close(fig)

    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(pd.to_datetime(monthly["reporting_month"]), monthly["dpd_30plus_pct"], label="30+ DPD")
    ax.plot(pd.to_datetime(monthly["reporting_month"]), monthly["dpd_90plus_pct"], label="90+ DPD")
    ax.set_title("Descriptive delinquency trend in the selected Fannie Mae panels")
    ax.set_ylabel("Share of observed loan-month rows, %")
    ax.set_xlabel("Reporting month")
    ax.legend()
    fig.autofmt_xdate(); fig.tight_layout(); fig.savefig(args.figures_dir / "05_calendar_month_delinquency_trend.png", dpi=180); plt.close(fig)

    metadata = {
        "version": "fannie_eda_v01",
        "cohorts": list(COHORTS),
        "unit_of_analysis": "loan-month",
        "total_loan_month_rows": int(overview["loan_month_rows"].sum()),
        "notes": [
            "All summaries use processed Fannie Mae panels only.",
            "Outcome rates use only non-censored eligible observations.",
            "Calendar trend is compositional across the selected acquisition cohorts and is not a US market-wide rate."
        ],
    }
    (args.reports_dir / "eda_metadata.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
