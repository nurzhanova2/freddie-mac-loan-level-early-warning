#!/usr/bin/env python3
"""Build versioned 3/6/12-month outcome files for Q1 horizon sensitivity."""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path


COHORTS = ("2006Q1", "2008Q1", "2012Q1", "2016Q1", "2020Q1", "2022Q1", "2024Q1")
MINIMUM_FREE_GIB = 6


def main() -> None:
    repo = Path(__file__).resolve().parents[2]
    for cohort in COHORTS:
        output = repo / f"fannie_mae/data/processed/{cohort}_outcomes_horizon_v02.parquet"
        report = repo / f"fannie_mae/reports/{cohort}_outcome_horizon_qa_v02.json"
        if output.is_file() and report.is_file():
            print(f"SKIP {cohort}: complete", flush=True)
            continue
        free_gib = shutil.disk_usage(repo).free / 1024**3
        if free_gib < MINIMUM_FREE_GIB:
            raise RuntimeError(f"Stopping before {cohort}: only {free_gib:.2f} GiB free")
        print(f"BUILD {cohort}; {free_gib:.2f} GiB free", flush=True)
        subprocess.run([
            sys.executable, "src/fannie_mae/build_fannie_outcomes.py",
            "--panel", f"fannie_mae/data/processed/{cohort}_monthly_panel_base.parquet",
            "--events", f"fannie_mae/data/interim/{cohort}_event_metadata.parquet",
            "--output", str(output), "--report", str(report),
            "--temp-dir", f"fannie_mae/data/interim/duckdb_horizon_{cohort}",
            "--threads", "2",
        ], cwd=repo, check=True)
        print(f"COMPLETE {cohort}", flush=True)


if __name__ == "__main__":
    main()
