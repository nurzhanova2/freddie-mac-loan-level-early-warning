#!/usr/bin/env python3
"""Summarise raw-archive validation evidence for the Q3 robustness extension."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--reports-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--cohorts", nargs="+", required=True)
    args = parser.parse_args()

    rows = []
    for cohort in args.cohorts:
        report_path = args.reports_dir / f"{cohort}_raw_validation.json"
        report = json.loads(report_path.read_text(encoding="utf-8"))
        rows.append({
            "acquisition_cohort": cohort,
            "compressed_bytes": report["compressed_bytes"],
            "uncompressed_bytes": report["uncompressed_bytes"],
            "rows": report["rows"],
            "expected_columns": report["expected_columns"],
            "malformed_rows": report["malformed_rows"],
            "blank_key_rows": report["blank_key_rows"],
            "adjacent_duplicate_loan_month_keys": report["adjacent_duplicate_loan_month_keys"],
            "raw_period_min": report["raw_period_min"],
            "raw_period_max": report["raw_period_max"],
            "row_order_status": report["row_order_status"],
            "validation_status": report["validation_status"],
            "sha256": report["sha256"],
        })

    frame = pd.DataFrame(rows)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    frame.to_csv(args.output_dir / "q3_archive_audit_v01.csv", index=False)
    summary = {
        "cohorts": args.cohorts,
        "cohort_count": len(args.cohorts),
        "total_rows": int(frame["rows"].sum()),
        "all_archives_passed": bool((frame["validation_status"] == "pass").all()),
        "total_malformed_rows": int(frame["malformed_rows"].sum()),
        "total_blank_key_rows": int(frame["blank_key_rows"].sum()),
        "total_adjacent_duplicate_keys": int(frame["adjacent_duplicate_loan_month_keys"].sum()),
        "interpretation": "The audit tests ZIP readability, field count, non-empty keys, and adjacent duplicate keys. It does not by itself establish global key uniqueness in files that are not key-sorted.",
    }
    (args.output_dir / "q3_archive_audit_v01_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
