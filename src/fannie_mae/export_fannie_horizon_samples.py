#!/usr/bin/env python3
"""Export deterministic 1% natural-rate samples for 3/6/12-month comparison."""
from __future__ import annotations

import argparse
import csv
from pathlib import Path

import duckdb


COHORTS = ("2006Q1", "2008Q1", "2012Q1", "2016Q1", "2020Q1", "2022Q1", "2024Q1")
TARGETS = (
    "formal_adverse_3m", "formal_adverse_6m", "formal_adverse_12m",
    "early_deterioration_3m", "early_deterioration_6m", "early_deterioration_12m",
)
FEATURES = """p.original_interest_rate, p.original_upb, p.original_loan_term,
p.original_loan_to_value_ratio_ltv, p.original_combined_loan_to_value_ratio_cltv,
p.number_of_borrowers, p.debt_to_income_dti, p.borrower_credit_score_at_origination,
p.co_borrower_credit_score_at_origination, p.mortgage_insurance_percentage,
p.current_interest_rate, p.current_actual_upb, p.loan_age,
p.remaining_months_to_legal_maturity, p.remaining_months_to_maturity,
p.channel, p.first_time_home_buyer_indicator, p.loan_purpose, p.property_type,
p.number_of_units, p.occupancy_status, p.property_state, p.amortization_type,
p.current_loan_delinquency_status, p.modification_flag"""
SPLITS = {
    "train": ("2006-01-01", "2016-12-01"),
    "validation": ("2017-01-01", "2020-12-01"),
    "out_of_time_test": ("2021-01-01", "2025-03-01"),
}


def file_list(directory: Path, suffix: str) -> str:
    return "[" + ", ".join(repr(str(directory / f"{cohort}_{suffix}")) for cohort in COHORTS) + "]"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", choices=TARGETS, required=True)
    parser.add_argument("--processed-dir", type=Path, default=Path("fannie_mae/data/processed"))
    parser.add_argument("--output-dir", type=Path, default=Path("fannie_mae/data/horizon_sensitivity_v01"))
    args = parser.parse_args()

    con = duckdb.connect()
    con.execute("SET threads = 4")
    con.execute(f"""CREATE VIEW panel AS
        SELECT *, regexp_extract(filename, '([0-9]{{4}}Q[1-4])_', 1) AS acquisition_cohort
        FROM read_parquet({file_list(args.processed_dir, 'monthly_panel_base.parquet')}, filename=true)""")
    con.execute(f"""CREATE VIEW outcomes AS
        SELECT *, regexp_extract(filename, '([0-9]{{4}}Q[1-4])_', 1) AS acquisition_cohort
        FROM read_parquet({file_list(args.processed_dir, 'outcomes_horizon_v02.parquet')}, filename=true)""")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    rows = []
    for split, (start, end) in SPLITS.items():
        condition = "hash(loan_identifier, monthly_reporting_period) % 10000 < 100"
        count, events = con.execute(f"""SELECT count(*), sum({args.target})
            FROM outcomes WHERE {args.target} IS NOT NULL
              AND monthly_reporting_period BETWEEN DATE '{start}' AND DATE '{end}'
              AND {condition}""").fetchone()
        output = args.output_dir / f"{args.target}_{split}_sample_v01.parquet"
        con.execute(f"""COPY (
            SELECT o.loan_identifier, o.monthly_reporting_period, o.acquisition_cohort,
              o.{args.target} AS label, '{split}' AS split, {FEATURES}
            FROM outcomes o JOIN panel p USING (acquisition_cohort, loan_identifier, monthly_reporting_period)
            WHERE o.{args.target} IS NOT NULL
              AND o.monthly_reporting_period BETWEEN DATE '{start}' AND DATE '{end}'
              AND {condition}
        ) TO {repr(str(output))} (FORMAT PARQUET, COMPRESSION ZSTD)""")
        rows.append({
            "target": args.target, "split": split, "start": start, "end": end,
            "hash_threshold": 100, "rows": int(count), "events": int(events or 0),
            "event_rate_pct": round(100 * (events or 0) / count, 6) if count else 0,
            "path": str(output),
        })
        print(f"EXPORTED {args.target} {split}: {count:,} rows", flush=True)
    manifest = args.output_dir / f"{args.target}_sample_manifest_v01.csv"
    with manifest.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    con.close()


if __name__ == "__main__":
    main()
