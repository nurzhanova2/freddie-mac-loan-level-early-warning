#!/usr/bin/env python3
"""Validate pipe-delimited Freddie Mac origination and performance files."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path


def profile(path: Path, expected_columns: int, key_columns: tuple[int, ...]) -> dict:
    column_counts: Counter[int] = Counter()
    rows = 0
    blank_rows = 0
    keys: Counter[tuple[str, ...]] = Counter()
    with path.open("r", encoding="utf-8", newline="") as file:
        reader = csv.reader(file, delimiter="|")
        for record in reader:
            if not record or not any(value.strip() for value in record):
                blank_rows += 1
                continue
            rows += 1
            column_counts[len(record)] += 1
            if len(record) >= max(key_columns):
                keys[tuple(record[index - 1].strip() for index in key_columns)] += 1
    duplicate_keys = sum(count - 1 for count in keys.values() if count > 1)
    return {
        "path": path.as_posix(),
        "rows": rows,
        "blank_rows": blank_rows,
        "expected_columns": expected_columns,
        "observed_column_counts": dict(sorted(column_counts.items())),
        "rows_with_unexpected_column_count": sum(
            count for columns, count in column_counts.items() if columns != expected_columns
        ),
        "distinct_keys": len(keys),
        "duplicate_key_rows": duplicate_keys,
    }


def loan_identifiers(path: Path, identifier_column: int) -> set[str]:
    identifiers: set[str] = set()
    with path.open("r", encoding="utf-8", newline="") as file:
        reader = csv.reader(file, delimiter="|")
        for record in reader:
            if len(record) >= identifier_column:
                value = record[identifier_column - 1].strip()
                if value:
                    identifiers.add(value)
    return identifiers


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--origination", required=True, type=Path)
    parser.add_argument("--performance", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    origination_ids = loan_identifiers(args.origination, 20)
    performance_ids = loan_identifiers(args.performance, 1)
    result = {
        "origination": profile(args.origination, 31, (20,)),
        "performance": profile(args.performance, 35, (1, 2)),
        "cross_file_join_check": {
            "origination_loan_identifiers": len(origination_ids),
            "performance_loan_identifiers": len(performance_ids),
            "overlapping_loan_identifiers": len(origination_ids & performance_ids),
            "suitable_for_loan_month_panel": bool(origination_ids & performance_ids),
        },
        "interpretation": (
            "A valid analytical vintage requires origination and performance files "
            "from the same downloaded sample/full vintage."
        ),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
