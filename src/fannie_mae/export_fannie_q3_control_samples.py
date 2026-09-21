#!/usr/bin/env python3
"""Export deterministic natural-rate Q3 samples for frozen-model evaluation."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import duckdb


COHORTS = ("2006Q3", "2008Q3", "2012Q3", "2014Q3", "2016Q3", "2018Q3", "2020Q3", "2022Q3", "2024Q3")
FEATURES = """p.original_interest_rate, p.original_upb, p.original_loan_term,
p.original_loan_to_value_ratio_ltv, p.original_combined_loan_to_value_ratio_cltv,
p.number_of_borrowers, p.debt_to_income_dti, p.borrower_credit_score_at_origination,
p.co_borrower_credit_score_at_origination, p.mortgage_insurance_percentage,
p.current_interest_rate, p.current_actual_upb, p.loan_age,
p.remaining_months_to_legal_maturity, p.remaining_months_to_maturity,
p.channel, p.first_time_home_buyer_indicator, p.loan_purpose, p.property_type,
p.number_of_units, p.occupancy_status, p.property_state, p.amortization_type,
p.current_loan_delinquency_status, p.modification_flag"""


def paths(directory: Path, suffix: str) -> str:
    return "[" + ", ".join(repr(str(directory / f"{c}_{suffix}")) for c in COHORTS) + "]"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", choices=("formal_adverse_6m", "early_deterioration_6m"), required=True)
    parser.add_argument("--processed-dir", type=Path, default=Path("fannie_mae/data/processed"))
    parser.add_argument("--output-dir", type=Path, default=Path("fannie_mae/data/q3_control_samples_v01"))
    parser.add_argument("--sample-pct", type=float, default=1.0)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    sample = args.output_dir / f"{args.target}_q3_control_sample_v01.parquet"
    con = duckdb.connect()
    con.execute("SET threads = 2")
    con.execute(f"CREATE VIEW panel AS SELECT *, regexp_extract(filename, '([0-9]{{4}}Q[1-4])_', 1) AS acquisition_cohort FROM read_parquet({paths(args.processed_dir, 'monthly_panel_base.parquet')}, filename=true)")
    con.execute(f"CREATE VIEW outcomes AS SELECT *, regexp_extract(filename, '([0-9]{{4}}Q[1-4])_', 1) AS acquisition_cohort FROM read_parquet({paths(args.processed_dir, 'outcomes_v01.parquet')}, filename=true)")
    denominator = round(100 / args.sample_pct)
    con.execute(f"""COPY (
        SELECT o.loan_identifier, o.monthly_reporting_period, o.acquisition_cohort,
          o.{args.target} AS label, {FEATURES}
        FROM outcomes o JOIN panel p USING (acquisition_cohort, loan_identifier, monthly_reporting_period)
        WHERE o.{args.target} IS NOT NULL
          AND hash(o.loan_identifier, o.monthly_reporting_period) % {denominator} = 0
    ) TO {repr(str(sample))} (FORMAT PARQUET, COMPRESSION ZSTD)""")
    rows, events = con.execute("SELECT count(*), sum(label) FROM read_parquet(?)", [str(sample)]).fetchone()
    by_cohort = con.execute("SELECT acquisition_cohort, count(*) AS rows, sum(label) AS events FROM read_parquet(?) GROUP BY 1 ORDER BY 1", [str(sample)]).fetchdf()
    by_cohort.to_csv(args.output_dir / f"{args.target}_q3_control_sample_by_cohort_v01.csv", index=False)
    (args.output_dir / f"{args.target}_q3_control_sample_manifest_v01.json").write_text(json.dumps({
        "target": args.target, "sampling": f"deterministic hash, {args.sample_pct}% natural-rate sample",
        "cohorts": COHORTS, "rows": int(rows), "events": int(events), "path": str(sample),
    }, indent=2) + "\n")
    con.close()


if __name__ == "__main__":
    main()
