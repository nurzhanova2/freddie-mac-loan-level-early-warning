#!/usr/bin/env python3
"""Validate the structure and key ordering of a Fannie Mae quarterly ZIP file."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import zipfile
from datetime import date
from pathlib import Path


EXPECTED_COLUMNS = 113


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--report", required=True, type=Path)
    parser.add_argument("--manifest", required=True, type=Path)
    args = parser.parse_args()

    with zipfile.ZipFile(args.source) as archive:
        members = [item for item in archive.infolist() if not item.is_dir()]
        if len(members) != 1:
            raise ValueError(f"Expected one CSV member, found {len(members)}.")
        member = members[0]
        rows = malformed = blank_keys = duplicate_keys = ordering_violations = 0
        loan_count = 0
        first_period = last_period = None
        previous_key: tuple[str, str] | None = None
        previous_loan: str | None = None
        with archive.open(member) as binary:
            reader = csv.reader((line.decode("utf-8") for line in binary), delimiter="|")
            for row in reader:
                rows += 1
                if len(row) != EXPECTED_COLUMNS:
                    malformed += 1
                    continue
                loan_id, period = row[1].strip(), row[2].strip()
                if not loan_id or not period:
                    blank_keys += 1
                    continue
                key = (loan_id, period)
                if previous_key is not None:
                    if key == previous_key:
                        duplicate_keys += 1
                    elif key < previous_key:
                        ordering_violations += 1
                if loan_id != previous_loan:
                    loan_count += 1
                    previous_loan = loan_id
                previous_key = key
                period_key = (period[2:], period[:2])
                first_period = period if first_period is None or period_key < (first_period[2:], first_period[:2]) else first_period
                last_period = period if last_period is None or period_key > (last_period[2:], last_period[:2]) else last_period

    report = {
        "source": args.source.as_posix(),
        "zip_member": member.filename,
        "compressed_bytes": args.source.stat().st_size,
        "uncompressed_bytes": member.file_size,
        "sha256": file_hash(args.source),
        "rows": rows,
        "expected_columns": EXPECTED_COLUMNS,
        "malformed_rows": malformed,
        "blank_key_rows": blank_keys,
        "adjacent_duplicate_loan_month_keys": duplicate_keys,
        "loan_month_key_ordering_violations": ordering_violations,
        "loan_identifier_runs": loan_count,
        "raw_period_min": first_period,
        "raw_period_max": last_period,
        "row_order_status": "monotonic" if not ordering_violations else "non_monotonic_not_a_schema_error",
        "validation_status": "pass" if not any((malformed, blank_keys, duplicate_keys)) else "review_required",
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    args.manifest.parent.mkdir(parents=True, exist_ok=True)
    with args.manifest.open("w", newline="", encoding="utf-8") as target:
        writer = csv.DictWriter(target, fieldnames=["manifest_date", "relative_path", "source", "bytes", "sha256", "zip_member", "uncompressed_bytes", "rows", "status"])
        writer.writeheader()
        writer.writerow({
            "manifest_date": date.today().isoformat(),
            "relative_path": args.source.as_posix(),
            "source": "Fannie Mae Data Dynamics, Single-Family Loan Performance Primary Dataset",
            "bytes": args.source.stat().st_size,
            "sha256": report["sha256"],
            "zip_member": member.filename,
            "uncompressed_bytes": member.file_size,
            "rows": rows,
            "status": report["validation_status"],
        })


if __name__ == "__main__":
    main()
