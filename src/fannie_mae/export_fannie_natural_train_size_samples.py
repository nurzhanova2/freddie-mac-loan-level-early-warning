#!/usr/bin/env python3
"""Export nested, natural-rate train samples for the fixed sensitivity protocol."""
from __future__ import annotations

import argparse
import csv
from pathlib import Path

import duckdb

COHORTS = ("2006Q1", "2008Q1", "2012Q1", "2016Q1", "2020Q1", "2022Q1", "2024Q1")
SHARES = (1, 5, 10, 25)
FEATURES = """p.original_interest_rate, p.original_upb, p.original_loan_term,
p.original_loan_to_value_ratio_ltv, p.original_combined_loan_to_value_ratio_cltv,
p.number_of_borrowers, p.debt_to_income_dti, p.borrower_credit_score_at_origination,
p.co_borrower_credit_score_at_origination, p.mortgage_insurance_percentage,
p.current_interest_rate, p.current_actual_upb, p.loan_age,
p.remaining_months_to_legal_maturity, p.remaining_months_to_maturity,
p.channel, p.first_time_home_buyer_indicator, p.loan_purpose, p.property_type,
p.number_of_units, p.occupancy_status, p.property_state, p.amortization_type,
p.current_loan_delinquency_status, p.modification_flag"""


def file_list(directory: Path, suffix: str) -> str:
    return "[" + ", ".join(repr(str(directory / f"{cohort}_{suffix}")) for cohort in COHORTS) + "]"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", choices=("formal_adverse_6m", "early_deterioration_6m"), required=True)
    parser.add_argument("--processed-dir", type=Path, default=Path("fannie_mae/data/processed"))
    parser.add_argument("--output-dir", type=Path, default=Path("fannie_mae/data/train_size_sensitivity_v01"))
    parser.add_argument("--shares", nargs="+", type=int, choices=SHARES, default=list(SHARES))
    parser.add_argument("--dry-run", action="store_true", help="write the manifest only; do not export parquet files")
    args = parser.parse_args()

    con = duckdb.connect()
    con.execute("PRAGMA threads=4")
    con.execute(f"""CREATE VIEW panel AS
        SELECT *, regexp_extract(filename, '([0-9]{{4}}Q[1-4])_', 1) AS acquisition_cohort
        FROM read_parquet({file_list(args.processed_dir, 'monthly_panel_base.parquet')}, filename=true)""")
    con.execute(f"""CREATE VIEW outcomes AS
        SELECT *, regexp_extract(filename, '([0-9]{{4}}Q[1-4])_', 1) AS acquisition_cohort
        FROM read_parquet({file_list(args.processed_dir, 'outcomes_v01.parquet')}, filename=true)""")
    con.execute(f"""CREATE VIEW eligible AS
        SELECT loan_identifier, monthly_reporting_period, acquisition_cohort, {args.target} AS label
        FROM outcomes
        WHERE {args.target} IS NOT NULL
          AND monthly_reporting_period >= DATE '2006-01-01'
          AND monthly_reporting_period <= DATE '2016-12-01'""")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    manifest = args.output_dir / f"{args.target}_natural_train_size_manifest_v01.csv"
    existing: dict[int, dict[str, object]] = {}
    if manifest.exists():
        with manifest.open(newline="") as handle:
            existing = {int(row["share_pct"]): row for row in csv.DictReader(handle)}
    rows = []
    for share in args.shares:
        threshold = share * 100
        condition = f"hash(loan_identifier, monthly_reporting_period) % 10000 < {threshold}"
        count, events = con.execute(f"SELECT count(*), sum(label) FROM eligible WHERE {condition}").fetchone()
        path = args.output_dir / f"{args.target}_train_natural_{share:02d}pct_v01.parquet"
        if not args.dry_run:
            con.execute(f"""COPY (
                SELECT e.loan_identifier, e.monthly_reporting_period, e.acquisition_cohort,
                       e.label, 'train' AS split, {FEATURES}
                FROM eligible e JOIN panel p USING (acquisition_cohort, loan_identifier, monthly_reporting_period)
                WHERE {condition}
            ) TO {repr(str(path))} (FORMAT PARQUET, COMPRESSION ZSTD)""")
        rows.append({"target": args.target, "share_pct": share, "hash_threshold": threshold,
                     "rows": int(count), "events": int(events or 0),
                     "event_rate_pct": round(100 * (events or 0) / count, 6) if count else 0,
                     "path": str(path), "exported": not args.dry_run})

    existing.update({int(row["share_pct"]): row for row in rows})
    with manifest.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(existing[share] for share in sorted(existing))


if __name__ == "__main__":
    main()
