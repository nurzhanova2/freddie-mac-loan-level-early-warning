#!/usr/bin/env python3
"""Run compact, sequential preparation for the remaining Q3 robustness cohorts."""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path


COHORTS = ("2012Q3", "2014Q3", "2016Q3", "2018Q3", "2020Q3", "2022Q3")
MINIMUM_FREE_GIB = 6


def run(command: list[str]) -> None:
    print("RUN:", " ".join(command), flush=True)
    subprocess.run(command, check=True)


def ensure_space(repo: Path) -> None:
    free_gib = shutil.disk_usage(repo).free / 1024**3
    print(f"Available space: {free_gib:.2f} GiB", flush=True)
    if free_gib < MINIMUM_FREE_GIB:
        raise RuntimeError(
            f"Stopping before the next cohort: {free_gib:.2f} GiB free is below "
            f"the {MINIMUM_FREE_GIB} GiB safety threshold."
        )


def main() -> None:
    repo = Path(__file__).resolve().parents[2]
    glossary = repo / "fannie_mae/docs/sources/crt-file-layout-and-glossary.xlsx"
    for cohort in COHORTS:
        panel = repo / f"fannie_mae/data/processed/{cohort}_monthly_panel_base.parquet"
        events = repo / f"fannie_mae/data/interim/{cohort}_event_metadata.parquet"
        outcome = repo / f"fannie_mae/data/processed/{cohort}_outcomes_v01.parquet"
        panel_report = repo / f"fannie_mae/reports/{cohort}_cleaning_and_panel.json"
        outcome_report = repo / f"fannie_mae/reports/{cohort}_outcome_qa_v01.json"
        if panel.is_file() and events.is_file() and outcome.is_file() and panel_report.is_file() and outcome_report.is_file():
            print(f"SKIP {cohort}: complete", flush=True)
            continue
        ensure_space(repo)
        year = cohort[:4]
        if not (panel.is_file() and events.is_file() and panel_report.is_file()):
            run([
                sys.executable, "src/fannie_mae/build_fannie_monthly_panel.py",
                "--source", f"fannie_mae/data/raw/{cohort}/{cohort}.zip",
                "--glossary", str(glossary),
                "--dictionary", f"fannie_mae/data/dictionaries/{year}q3_field_dictionary.csv",
                "--panel", str(panel), "--event-metadata", str(events),
                "--report", str(panel_report), "--chunksize", "50000",
            ])
        if not (outcome.is_file() and outcome_report.is_file()):
            run([
                sys.executable, "src/fannie_mae/build_fannie_outcomes.py",
                "--panel", str(panel), "--events", str(events),
                "--output", str(outcome), "--report", str(outcome_report),
                "--temp-dir", f"fannie_mae/data/interim/duckdb_q3_{cohort}",
                "--threads", "2",
            ])
        print(f"COMPLETE {cohort}", flush=True)


if __name__ == "__main__":
    main()
