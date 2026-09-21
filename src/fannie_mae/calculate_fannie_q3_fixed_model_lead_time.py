#!/usr/bin/env python3
"""Calculate observed lead time for Q3 alerts from frozen-model evaluation."""

from __future__ import annotations

import argparse
from pathlib import Path

import duckdb


COHORTS = ("2006Q3", "2008Q3", "2012Q3", "2014Q3", "2016Q3", "2018Q3", "2020Q3", "2022Q3", "2024Q3")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", choices=("formal_adverse_6m", "early_deterioration_6m"), required=True)
    parser.add_argument("--processed-dir", type=Path, default=Path("fannie_mae/data/processed"))
    parser.add_argument("--reports-dir", type=Path, default=Path("fannie_mae/reports/q3_fixed_models_v01"))
    args = parser.parse_args()
    paths = "[" + ", ".join(repr(str(args.processed_dir / f"{c}_monthly_panel_base.parquet")) for c in COHORTS) + "]"
    alerts = args.reports_dir / f"{args.target}_q3_fixed_model_alerts_v01.parquet"
    condition = "try_cast(p.current_loan_delinquency_status AS INTEGER) BETWEEN 3 AND 98" if args.target == "formal_adverse_6m" else "try_cast(p.current_loan_delinquency_status AS INTEGER) BETWEEN 1 AND 98"
    con = duckdb.connect()
    con.execute("SET threads = 2")
    result = con.execute(f"""
        WITH alerts AS (
          SELECT model, capacity, acquisition_cohort, loan_identifier, monthly_reporting_period AS alert_month
          FROM read_parquet({repr(str(alerts))}) WHERE label = 1
        ), panel AS (
          SELECT *, regexp_extract(filename, '([0-9]{{4}}Q[1-4])_', 1) AS acquisition_cohort
          FROM read_parquet({paths}, filename=true)
        ), hits AS (
          SELECT a.model, a.capacity, a.acquisition_cohort, a.loan_identifier, a.alert_month,
            min(date_diff('month', a.alert_month, p.monthly_reporting_period)) AS months_to_event
          FROM alerts a JOIN panel p USING (acquisition_cohort, loan_identifier)
          WHERE p.monthly_reporting_period > a.alert_month
            AND p.monthly_reporting_period <= a.alert_month + INTERVAL 6 MONTH
            AND {condition}
          GROUP BY 1, 2, 3, 4, 5
        )
        SELECT model, capacity * 100 AS alert_capacity_pct,
          count(*) AS alerted_events_with_observed_event,
          round(avg(months_to_event), 3) AS mean_months_to_event,
          quantile_cont(months_to_event, 0.5) AS median_months_to_event,
          min(months_to_event) AS min_months_to_event,
          max(months_to_event) AS max_months_to_event
        FROM hits GROUP BY 1, 2 ORDER BY 1
    """).fetchdf()
    result.insert(0, "target", args.target)
    result.to_csv(args.reports_dir / f"{args.target}_q3_fixed_model_lead_time_v01.csv", index=False)
    con.close()


if __name__ == "__main__":
    main()
