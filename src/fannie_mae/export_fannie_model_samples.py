#!/usr/bin/env python3
"""Create deterministic CPU-feasible stage-13 samples from the temporal split."""
from __future__ import annotations
import argparse, json
from pathlib import Path
import duckdb

COHORTS = ("2006Q1", "2008Q1", "2012Q1", "2016Q1", "2020Q1", "2022Q1", "2024Q1")
FEATURES = """p.original_interest_rate, p.original_upb, p.original_loan_term,
p.original_loan_to_value_ratio_ltv, p.original_combined_loan_to_value_ratio_cltv,
p.number_of_borrowers, p.debt_to_income_dti, p.borrower_credit_score_at_origination,
p.co_borrower_credit_score_at_origination, p.mortgage_insurance_percentage,
p.current_interest_rate, p.current_actual_upb, p.loan_age,
p.remaining_months_to_legal_maturity, p.remaining_months_to_maturity,
p.channel, p.first_time_home_buyer_indicator, p.loan_purpose, p.property_type,
p.number_of_units, p.occupancy_status, p.property_state, p.amortization_type,
p.current_loan_delinquency_status, p.modification_flag"""

def files(directory: Path, suffix: str, cohorts: tuple[str, ...]) -> str:
    return "[" + ", ".join(repr(str(directory / f"{c}_{suffix}")) for c in cohorts) + "]"

def main() -> None:
    parser=argparse.ArgumentParser()
    parser.add_argument("--target", choices=["formal_adverse_6m", "early_deterioration_6m"], required=True)
    parser.add_argument("--processed-dir", type=Path, default=Path("fannie_mae/data/processed"))
    parser.add_argument("--output-dir", type=Path, default=Path("fannie_mae/data/model_samples_v01"))
    parser.add_argument("--cohorts", nargs="+", default=list(COHORTS))
    args=parser.parse_args(); args.output_dir.mkdir(parents=True, exist_ok=True)
    # Train retains roughly 0.6m rows per outcome; validation/test use an unbiased 1% hash sample.
    thresholds = {"formal_adverse_6m": (3000, 65), "early_deterioration_6m": (900, 68)}
    positive, negative = thresholds[args.target]
    con=duckdb.connect(); con.execute("PRAGMA threads=4")
    cohorts = tuple(args.cohorts)
    con.execute(f"CREATE VIEW panel AS SELECT *, regexp_extract(filename, '([0-9]{{4}}Q[1-4])_', 1) AS acquisition_cohort FROM read_parquet({files(args.processed_dir, 'monthly_panel_base.parquet', cohorts)}, filename=true)")
    con.execute(f"CREATE VIEW outcomes AS SELECT *, regexp_extract(filename, '([0-9]{{4}}Q[1-4])_', 1) AS acquisition_cohort FROM read_parquet({files(args.processed_dir, 'outcomes_v01.parquet', cohorts)}, filename=true)")
    outputs=[]
    for split in ("train", "validation", "out_of_time_test"):
        split_condition = {"train": "monthly_reporting_period < DATE '2017-01-01'", "validation": "monthly_reporting_period >= DATE '2017-01-01' AND monthly_reporting_period < DATE '2021-01-01'", "out_of_time_test": "monthly_reporting_period >= DATE '2021-01-01' AND monthly_reporting_period <= DATE '2025-09-01'"}[split]
        hash_condition = (f"((label=1 AND hash(loan_identifier, monthly_reporting_period) % 10000 < {positive}) OR (label=0 AND hash(loan_identifier, monthly_reporting_period) % 10000 < {negative}))"
                          if split == "train" else "hash(loan_identifier, monthly_reporting_period) % 100 < 1")
        source_hash_condition = hash_condition.replace("label", args.target)
        con.execute(f"""CREATE OR REPLACE TEMP VIEW selected AS
          SELECT loan_identifier, monthly_reporting_period, acquisition_cohort,
                 {args.target} AS label, '{split}' AS split
          FROM outcomes
          WHERE {args.target} IS NOT NULL AND {split_condition} AND {source_hash_condition}""")
        path=args.output_dir / f"{args.target}_{split}_sample_v01.parquet"
        con.execute(f"COPY (SELECT s.*, {FEATURES} FROM selected s JOIN panel p USING (acquisition_cohort, loan_identifier, monthly_reporting_period)) TO {repr(str(path))} (FORMAT PARQUET, COMPRESSION ZSTD)")
        row=con.execute("SELECT count(*) AS rows, sum(label) AS events FROM read_parquet(?)", [str(path)]).fetchone()
        outputs.append({"split": split, "path": str(path), "rows": int(row[0]), "events": int(row[1])})
    (args.output_dir / f"{args.target}_sample_manifest_v01.json").write_text(json.dumps({"target":args.target,"cohorts":cohorts,"sampling":"deterministic hash; train case-control, validation/test 1% natural-rate sample","outputs":outputs}, indent=2)+"\n")

if __name__ == '__main__': main()
