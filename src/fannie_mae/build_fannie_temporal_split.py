#!/usr/bin/env python3
"""Audit the strict chronological split without materialising a duplicate panel.

Outputs counts for the two six-month outcomes. The source processed panels stay
separate; a downstream model query can use the recorded split rule directly.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import duckdb
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd


COHORTS = ("2006Q1", "2008Q1", "2012Q1", "2016Q1", "2020Q1", "2022Q1", "2024Q1")
FEATURES = (
    "original_interest_rate", "original_upb", "original_loan_term",
    "original_loan_to_value_ratio_ltv", "original_combined_loan_to_value_ratio_cltv",
    "number_of_borrowers", "debt_to_income_dti", "borrower_credit_score_at_origination",
    "co_borrower_credit_score_at_origination", "mortgage_insurance_percentage",
    "current_interest_rate", "current_actual_upb", "loan_age",
    "remaining_months_to_legal_maturity", "remaining_months_to_maturity", "channel",
    "first_time_home_buyer_indicator", "loan_purpose", "property_type", "number_of_units",
    "occupancy_status", "property_state", "amortization_type",
    "current_loan_delinquency_status", "modification_flag",
)


def parquet_list(paths: list[str]) -> str:
    return "[" + ", ".join(repr(path) for path in paths) + "]"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--processed-dir", type=Path, default=Path("fannie_mae/data/processed"))
    parser.add_argument("--output-dir", type=Path, default=Path("fannie_mae/reports/splits"))
    parser.add_argument("--include-cohort-detail", action="store_true", help="recompute the additional cohort-level audit")
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    panel_paths = [str(args.processed_dir / f"{cohort}_monthly_panel_base.parquet") for cohort in COHORTS]
    outcome_paths = [str(args.processed_dir / f"{cohort}_outcomes_v01.parquet") for cohort in COHORTS]
    for path in panel_paths + outcome_paths:
        if not Path(path).exists():
            raise FileNotFoundError(path)

    con = duckdb.connect()
    con.execute("PRAGMA threads=4")
    panels = con.execute(f"SELECT * FROM read_parquet({parquet_list(panel_paths)}, union_by_name=true) LIMIT 0").fetchdf()
    missing_features = sorted(set(FEATURES) - set(panels.columns))
    if missing_features:
        raise ValueError(f"Feature fields absent from a panel: {missing_features}")
    con.execute(f"""
      CREATE VIEW outcomes AS
      SELECT *, regexp_extract(filename, '([0-9]{{4}}Q[1-4])_', 1) AS acquisition_cohort
      FROM read_parquet({parquet_list(outcome_paths)}, filename=true)
    """)

    result = con.execute("""
      WITH assigned AS (
        SELECT *,
          CASE
            WHEN monthly_reporting_period < DATE '2017-01-01' THEN 'train'
            WHEN monthly_reporting_period < DATE '2021-01-01' THEN 'validation'
            WHEN monthly_reporting_period <= DATE '2025-09-01' THEN 'out_of_time_test'
            ELSE 'excluded_incomplete_six_month_window'
          END AS split
        FROM outcomes
      ), long_labels AS (
        SELECT split, acquisition_cohort, loan_identifier, monthly_reporting_period,
               'formal_adverse_6m' AS target, formal_adverse_6m AS label FROM assigned
        UNION ALL
        SELECT split, acquisition_cohort, loan_identifier, monthly_reporting_period,
               'early_deterioration_6m' AS target, early_deterioration_6m AS label FROM assigned
      )
      SELECT split, target,
             count(*) AS candidate_loan_month_rows,
             count(DISTINCT loan_identifier) AS distinct_loans,
             count(*) FILTER (WHERE label IS NOT NULL) AS eligible_loan_month_rows,
             sum(CASE WHEN label = 1 THEN 1 ELSE 0 END) AS events,
             round(100.0 * avg(CASE WHEN label = 1 THEN 1 ELSE 0 END)
                   FILTER (WHERE label IS NOT NULL), 4) AS event_rate_pct
      FROM long_labels
      WHERE split <> 'excluded_incomplete_six_month_window'
      GROUP BY 1, 2
      ORDER BY CASE split WHEN 'train' THEN 1 WHEN 'validation' THEN 2 ELSE 3 END, target
    """).fetchdf()
    result.to_csv(args.output_dir / "fannie_temporal_split_v01_summary.csv", index=False)

    cohort_path = args.output_dir / "fannie_temporal_split_v01_by_cohort.csv"
    if args.include_cohort_detail or not cohort_path.exists():
        cohort_result = con.execute("""
          WITH assigned AS (
            SELECT *,
              CASE
                WHEN monthly_reporting_period < DATE '2017-01-01' THEN 'train'
                WHEN monthly_reporting_period < DATE '2021-01-01' THEN 'validation'
                WHEN monthly_reporting_period <= DATE '2025-09-01' THEN 'out_of_time_test'
                ELSE 'excluded_incomplete_six_month_window'
              END AS split
            FROM outcomes
          )
          SELECT split, acquisition_cohort,
                 count(*) AS candidate_loan_month_rows,
                 count(*) FILTER (WHERE formal_adverse_6m IS NOT NULL) AS formal_6m_eligible_rows,
                 count(*) FILTER (WHERE early_deterioration_6m IS NOT NULL) AS early_6m_eligible_rows
          FROM assigned
          WHERE split <> 'excluded_incomplete_six_month_window'
          GROUP BY 1, 2
          ORDER BY 1, 2
        """).fetchdf()
        cohort_result.to_csv(cohort_path, index=False)

    boundaries = pd.DataFrame([
        ("train", "2006-01-01", "2016-12-01"),
        ("validation", "2017-01-01", "2020-12-01"),
        ("out_of_time_test", "2021-01-01", "2025-09-01"),
    ], columns=["split", "first_reporting_month", "last_reporting_month"])
    candidate_counts = result[["split", "candidate_loan_month_rows"]].drop_duplicates()
    boundaries = boundaries.merge(candidate_counts, on="split", validate="one_to_one")
    if boundaries["candidate_loan_month_rows"].le(0).any():
        raise AssertionError("A temporal split contains no candidate rows")
    boundaries.to_csv(args.output_dir / "fannie_temporal_split_v01_boundary_audit.csv", index=False)

    figures_dir = args.output_dir.parent / "figures" / "splits"
    figures_dir.mkdir(parents=True, exist_ok=True)
    timeline = [
        ("Train", "2006-01-01", "2016-12-01", "#1f77b4"),
        ("Validation", "2017-01-01", "2020-12-01", "#ff7f0e"),
        ("Out-of-time test", "2021-01-01", "2025-09-01", "#2ca02c"),
    ]
    fig, ax = plt.subplots(figsize=(11, 2.8))
    for index, (name, start, end, colour) in enumerate(timeline):
        start_dt, end_dt = pd.Timestamp(start), pd.Timestamp(end) + pd.offsets.MonthEnd(1)
        ax.barh(index, (end_dt - start_dt).days, left=mdates.date2num(start_dt), color=colour, height=0.55)
        ax.text(mdates.date2num(start_dt + (end_dt - start_dt) / 2), index, name, ha="center", va="center", color="white", fontsize=10, weight="bold")
    ax.set_yticks([])
    ax.set_xlim(mdates.date2num(pd.Timestamp("2006-01-01")), mdates.date2num(pd.Timestamp("2026-03-01")))
    ax.xaxis_date(); ax.xaxis.set_major_locator(mdates.YearLocator(2)); ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax.set_title("Chronological split for the strict six-month early-warning evaluation")
    ax.axvline(mdates.date2num(pd.Timestamp("2025-09-01")), color="#333333", linestyle="--", linewidth=1)
    ax.text(mdates.date2num(pd.Timestamp("2025-09-01")), 2.45, "last prediction month", ha="right", va="bottom", fontsize=8)
    fig.tight_layout(); fig.savefig(figures_dir / "fannie_temporal_split_timeline_v01.png", dpi=180); plt.close(fig)

    metadata = {
        "version": "fannie_temporal_split_v01",
        "primary_horizon_months": 6,
        "reporting_data_cutoff": "2026-03-01",
        "strict_out_of_time_last_prediction_month": "2025-09-01",
        "cohorts": list(COHORTS),
        "model_features_verified_available": list(FEATURES),
        "notes": [
            "No duplicate model-ready parquet was materialised; the split is a reproducible rule over processed panels.",
            "Rows with a null target are excluded from target-specific fitting and evaluation.",
            "The split is chronological; loan identifiers are not model features."
        ],
        "boundary_audit": "fannie_temporal_split_v01_boundary_audit.csv",
        "model_input_contract": "fannie_mae/sql/fannie_model_input_v01.sql"
    }
    (args.output_dir / "fannie_temporal_split_v01_metadata.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
