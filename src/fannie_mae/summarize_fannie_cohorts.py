#!/usr/bin/env python3
"""Create a cohort-level QA and outcome summary from completed Fannie artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--reports-dir", required=True, type=Path)
    parser.add_argument("--cohorts", nargs="+", required=True)
    parser.add_argument("--csv-output", required=True, type=Path)
    parser.add_argument("--json-output", required=True, type=Path)
    args = parser.parse_args()

    rows = []
    for cohort in args.cohorts:
        raw = json.loads((args.reports_dir / "{}_raw_validation.json".format(cohort)).read_text())
        cleaned = json.loads((args.reports_dir / "{}_cleaning_and_panel.json".format(cohort)).read_text())
        outcomes = json.loads((args.reports_dir / "{}_outcome_qa_v01.json".format(cohort)).read_text())
        row = {
            "cohort": cohort,
            "raw_rows": raw["rows"],
            "panel_rows": cleaned["rows_written"],
            "raw_period_min": raw["raw_period_min"],
            "raw_period_max": raw["raw_period_max"],
            "raw_validation_status": raw["validation_status"],
        }
        for label, summary in outcomes["label_summaries"].items():
            prefix = label.replace("_", "_")
            row[prefix + "_labelled"] = summary["labelled_rows"]
            row[prefix + "_events"] = summary["positive_events"]
            row[prefix + "_event_rate"] = (
                summary["positive_events"] / summary["labelled_rows"]
                if summary["labelled_rows"] else None
            )
        rows.append(row)

    args.csv_output.parent.mkdir(parents=True, exist_ok=True)
    names = list(rows[0])
    with args.csv_output.open("w", newline="", encoding="utf-8") as target:
        writer = csv.DictWriter(target, fieldnames=names)
        writer.writeheader()
        writer.writerows(rows)

    total_panel_rows = sum(row["panel_rows"] for row in rows)
    summary = {
        "cohorts": args.cohorts,
        "cohort_count": len(rows),
        "total_panel_rows": total_panel_rows,
        "all_raw_validation_pass": all(row["raw_validation_status"] == "pass" for row in rows),
        "rows": rows,
    }
    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()

