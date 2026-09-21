#!/usr/bin/env python3
"""Clean Release 47 files and build a leakage-unlabelled loan-month panel.

The script intentionally does not construct outcomes or select model features.
Those operations belong to later, separately audited stages.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import unicodedata
from pathlib import Path

import pandas as pd
import yaml


def snake_case(value: str) -> str:
    ascii_value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode()
    return re.sub(r"_+", "_", re.sub(r"[^a-z0-9]+", "_", ascii_value.lower())).strip("_")


def read_headers(path: Path) -> list[str]:
    values = path.read_text(encoding="utf-8").strip().split("|")
    return [snake_case(value) for value in values]


def load_rules(path: Path) -> dict:
    with path.open(encoding="utf-8") as file:
        return yaml.safe_load(file)


def numeric_columns(dictionary: Path, component: str) -> set[str]:
    with dictionary.open(encoding="utf-8", newline="") as file:
        rows = csv.DictReader(file)
        return {
            snake_case(row["official_attribute_name"])
            for row in rows
            if row["dataset_component"] == component
            and row["technical_type_format"].startswith("Numeric")
        }


def validate_width(path: Path, width: int) -> None:
    with path.open(encoding="utf-8", newline="") as file:
        reader = csv.reader(file, delimiter="|")
        for line_number, row in enumerate(reader, start=1):
            if len(row) != width:
                raise ValueError(
                    f"{path}: line {line_number} has {len(row)} columns; expected {width}."
                )


def clean_frame(
    frame: pd.DataFrame,
    component: str,
    rules: dict,
    numeric_fields: set[str],
) -> tuple[pd.DataFrame, dict]:
    frame = frame.apply(lambda series: series.str.strip())
    blank_values = int(frame.eq("").sum().sum())
    frame = frame.replace("", pd.NA)
    null_code_counts: dict[str, int] = {}
    for column, values in rules["null_codes"].items():
        if column in frame.columns:
            mask = frame[column].isin(values)
            null_code_counts[column] = int(mask.sum())
            frame.loc[mask, column] = pd.NA
    invalid_numeric: dict[str, int] = {}
    for column in sorted(numeric_fields & set(frame.columns)):
        converted = pd.to_numeric(frame[column], errors="coerce")
        invalid_numeric[column] = int((frame[column].notna() & converted.isna()).sum())
        frame[column] = converted
    invalid_dates: dict[str, int] = {}
    for column in rules["date_columns"][component]:
        if column in frame.columns:
            converted = pd.to_datetime(frame[column], format="%Y%m", errors="coerce")
            invalid_dates[column] = int((frame[column].notna() & converted.isna()).sum())
            frame[column] = converted
    audit = {
        "input_rows": len(frame),
        "blank_values_converted_to_null": blank_values,
        "documented_null_codes_converted": null_code_counts,
        "invalid_numeric_values_converted_to_null": invalid_numeric,
        "invalid_date_values_converted_to_null": invalid_dates,
    }
    return frame, audit


def read_and_clean(
    source: Path,
    headers: list[str],
    component: str,
    rules: dict,
    dictionary: Path,
    chunksize: int | None = None,
):
    validate_width(source, len(headers))
    fields = numeric_columns(dictionary, component)
    reader = pd.read_csv(
        source, sep="|", names=headers, header=None, dtype="string",
        keep_default_na=False, chunksize=chunksize,
    )
    if chunksize is None:
        return clean_frame(reader, component, rules, fields)
    return ((clean_frame(chunk, component, rules, fields)) for chunk in reader)


def audit_keys(frame: pd.DataFrame, keys: list[str], label: str) -> dict:
    null_key_rows = int(frame[keys].isna().any(axis=1).sum())
    duplicate_rows = int(frame.duplicated(keys).sum())
    if null_key_rows or duplicate_rows:
        raise ValueError(
            f"{label} has {null_key_rows} null-key rows and {duplicate_rows} duplicate key rows."
        )
    return {"key_columns": keys, "null_key_rows": null_key_rows, "duplicate_key_rows": duplicate_rows}


def write_csv(frame: pd.DataFrame, destination: Path, include_header: bool) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(destination, index=False, mode="w" if include_header else "a", header=include_header)


def clean_origination(args: argparse.Namespace, rules: dict) -> None:
    headers = read_headers(args.origination_headers)
    frame, audit = read_and_clean(
        args.source, headers, "origination", rules, args.dictionary
    )
    audit["key_audit"] = audit_keys(frame, ["loan_identifier"], "origination")
    write_csv(frame, args.output, include_header=True)
    args.audit.write_text(json.dumps(audit, indent=2) + "\n", encoding="utf-8")


def clean_performance(args: argparse.Namespace, rules: dict) -> None:
    headers = read_headers(args.performance_headers)
    audits, first = [], True
    for chunk, audit in read_and_clean(
        args.source, headers, "monthly_performance", rules, args.dictionary, args.chunksize
    ):
        audits.append(audit)
        write_csv(chunk, args.output, include_header=first)
        first = False
    # Duplicate keys must be audited across chunks; this read is limited to two columns.
    key_frame = pd.read_csv(args.output, usecols=["loan_identifier", "period"])
    audit = {"chunks": audits, "key_audit": audit_keys(key_frame, ["loan_identifier", "period"], "performance")}
    args.audit.write_text(json.dumps(audit, indent=2) + "\n", encoding="utf-8")


def build_panel(args: argparse.Namespace) -> None:
    origination = pd.read_csv(args.origination, low_memory=False)
    audit_keys(origination, ["loan_identifier"], "clean origination")
    origination_ids = set(origination["loan_identifier"].astype(str))
    total_rows = 0
    unmatched_ids: set[str] = set()
    for performance in pd.read_csv(
        args.performance, usecols=["loan_identifier"], chunksize=args.chunksize, low_memory=False
    ):
        total_rows += len(performance)
        unmatched_ids.update(
            set(performance.loc[
                ~performance["loan_identifier"].astype(str).isin(origination_ids), "loan_identifier"
            ].astype(str))
        )
    if total_rows == 0:
        raise ValueError("Performance input contained no rows.")
    if unmatched_ids:
        result = {
            "performance_rows": total_rows,
            "matched_rows": "not_computed",
            "unmatched_loan_identifier_count": len(unmatched_ids),
            "panel_status": "invalid_input_pair",
        }
        args.audit.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
        raise ValueError(
            "Origination and performance files are not a complete matched pair; "
            "no analytical panel was created."
        )

    matched_rows, first = 0, True
    for performance in pd.read_csv(args.performance, chunksize=args.chunksize, low_memory=False):
        audit_keys(performance, ["loan_identifier", "period"], "clean performance chunk")
        panel = performance.merge(origination, on="loan_identifier", how="left", validate="many_to_one", indicator=True)
        matched_rows += int((panel["_merge"] == "both").sum())
        panel = panel.drop(columns="_merge")
        write_csv(panel, args.output, include_header=first)
        first = False
    result = {
        "performance_rows": total_rows,
        "matched_rows": matched_rows,
        "unmatched_rows": total_rows - matched_rows,
        "unmatched_loan_identifier_count": len(unmatched_ids),
        "panel_status": "ready_for_next_stage",
    }
    args.audit.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")


def parser() -> argparse.ArgumentParser:
    root = Path(".")
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--dictionary", type=Path, default=root / "docs/data_dictionary_release_47.csv")
    common.add_argument("--rules", type=Path, default=root / "config/field_rules_release_47.yml")
    common.add_argument("--origination-headers", type=Path, default=root / "docs/sources/file_headers_july_2026/origination_data_file_header.txt")
    common.add_argument("--performance-headers", type=Path, default=root / "docs/sources/file_headers_july_2026/performance_data_file_header.txt")
    root_parser = argparse.ArgumentParser(description=__doc__)
    commands = root_parser.add_subparsers(dest="command", required=True)
    for command in ("clean-origination", "clean-performance"):
        sub = commands.add_parser(command, parents=[common])
        sub.add_argument("--source", type=Path, required=True)
        sub.add_argument("--output", type=Path, required=True)
        sub.add_argument("--audit", type=Path, required=True)
        if command == "clean-performance":
            sub.add_argument("--chunksize", type=int, default=500_000)
    panel = commands.add_parser("build-panel")
    panel.add_argument("--origination", type=Path, required=True)
    panel.add_argument("--performance", type=Path, required=True)
    panel.add_argument("--output", type=Path, required=True)
    panel.add_argument("--audit", type=Path, required=True)
    panel.add_argument("--chunksize", type=int, default=500_000)
    return root_parser


def main() -> None:
    args = parser().parse_args()
    if args.command == "build-panel":
        build_panel(args)
    else:
        rules = load_rules(args.rules)
        if args.command == "clean-origination":
            clean_origination(args, rules)
        else:
            clean_performance(args, rules)


if __name__ == "__main__":
    main()
