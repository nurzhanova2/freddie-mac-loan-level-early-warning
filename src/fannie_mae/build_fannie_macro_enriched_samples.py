#!/usr/bin/env python3
"""Join a audited point-in-time macro mart to the frozen Fannie v01 samples.

This script deliberately performs no fitting.  It creates an additive feature
branch and an audit report so that baseline and macro-enriched models can be
trained from exactly the same temporal splits in a later, controlled step.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


TARGETS = ("formal_adverse_6m", "early_deterioration_6m")
SPLITS = ("train", "validation", "out_of_time_test")
NATIONAL_FAMILIES = ("fedfunds", "unemployment")
REGIONAL_FAMILIES = ("state_unemployment", "state_hpi")
TERRITORIES_WITH_POSSIBLY_UNAVAILABLE_SERIES = {"GU", "PR", "VI"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--macro-mart",
        type=Path,
        required=True,
        help="CSV emitted by build_fannie_macro_asof_context.py.",
    )
    parser.add_argument("--samples-dir", type=Path, default=Path("fannie_mae/data/model_samples_v01"))
    parser.add_argument("--output-dir", type=Path, default=Path("fannie_mae/data/macro_enriched_v01"))
    parser.add_argument(
        "--audit-output",
        type=Path,
        default=Path("fannie_mae/reports/macro_enriched_v01/macro_join_audit_v01.json"),
    )
    parser.add_argument("--overwrite", action="store_true")
    return parser.parse_args()


def read_and_audit_mart(path: Path) -> pd.DataFrame:
    mart = pd.read_csv(path)
    required = {
        "reporting_month", "feature_family", "geography", "series_id",
        "requested_vintage_date", "source_observation_date", "value",
    }
    missing = required - set(mart.columns)
    if missing:
        raise ValueError(f"Macro mart is missing required columns: {sorted(missing)}")
    mart["reporting_month"] = pd.to_datetime(mart["reporting_month"] + "-01")
    mart["requested_vintage_date"] = pd.to_datetime(mart["requested_vintage_date"])
    mart["source_observation_date"] = pd.to_datetime(mart["source_observation_date"], errors="coerce")
    later_vintage = mart.requested_vintage_date > mart.reporting_month
    later_observation = mart.source_observation_date > mart.reporting_month
    if later_vintage.any() or later_observation.any():
        raise ValueError(
            "Point-in-time failure: a vintage or source observation follows its reporting month."
        )
    duplicated = mart.duplicated(
        subset=["reporting_month", "feature_family", "geography", "series_id"], keep=False
    )
    if duplicated.any():
        raise ValueError("Macro mart contains duplicate point-in-time series records.")
    return mart


def pivot_mart(mart: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    national = mart.loc[
        (mart.geography == "US") & mart.feature_family.isin(NATIONAL_FAMILIES),
        ["reporting_month", "feature_family", "value"],
    ].pivot(index="reporting_month", columns="feature_family", values="value")
    national = national.rename(columns={"fedfunds": "fedfunds_asof", "unemployment": "unemployment_us_asof"})

    regional = mart.loc[
        mart.feature_family.isin(REGIONAL_FAMILIES),
        ["reporting_month", "geography", "feature_family", "value"],
    ].pivot(index=["reporting_month", "geography"], columns="feature_family", values="value")
    regional = regional.rename(columns={
        "state_unemployment": "state_unemployment_asof",
        "state_hpi": "state_hpi_asof",
    })
    return national.reset_index(), regional.reset_index()


def audit_join(frame: pd.DataFrame) -> dict[str, object]:
    macro_columns = [
        "fedfunds_asof", "unemployment_us_asof", "state_unemployment_asof", "state_hpi_asof",
    ]
    missing = {column: int(frame[column].isna().sum()) for column in macro_columns}
    territory_rows = frame.property_state.isin(TERRITORIES_WITH_POSSIBLY_UNAVAILABLE_SERIES)
    return {
        "rows": int(len(frame)),
        "score_month_min": str(frame.monthly_reporting_period.min().date()),
        "score_month_max": str(frame.monthly_reporting_period.max().date()),
        "macro_missing_values": missing,
        "territory_rows": int(territory_rows.sum()),
        "nonterritory_missing_regional_values": {
            column: int((frame.loc[~territory_rows, column].isna()).sum())
            for column in ("state_unemployment_asof", "state_hpi_asof")
        },
    }


def main() -> None:
    args = parse_args()
    mart = read_and_audit_mart(args.macro_mart)
    national, regional = pivot_mart(mart)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    audit: dict[str, object] = {
        "version": "macro_join_audit_v01",
        "macro_mart": str(args.macro_mart),
        "point_in_time_check": "passed",
        "outputs": {},
    }
    for target in TARGETS:
        for split in SPLITS:
            name = f"{target}_{split}_sample_v01.parquet"
            source = args.samples_dir / name
            destination = args.output_dir / name
            if destination.exists() and not args.overwrite:
                raise FileExistsError(f"Refusing to overwrite {destination}; pass --overwrite explicitly.")
            frame = pd.read_parquet(source)
            frame = frame.merge(national, how="left", left_on="monthly_reporting_period", right_on="reporting_month")
            frame = frame.drop(columns="reporting_month")
            frame = frame.merge(
                regional,
                how="left",
                left_on=["monthly_reporting_period", "property_state"],
                right_on=["reporting_month", "geography"],
            ).drop(columns=["reporting_month", "geography"])
            for column in ("state_unemployment_asof", "state_hpi_asof"):
                frame[f"{column}_available"] = frame[column].notna().astype("int8")
            frame.to_parquet(destination, index=False)
            audit["outputs"][f"{target}/{split}"] = audit_join(frame)
    args.audit_output.parent.mkdir(parents=True, exist_ok=True)
    args.audit_output.write_text(json.dumps(audit, indent=2) + "\n")
    print(f"Wrote macro-enriched samples to {args.output_dir}")
    print(f"Wrote join audit to {args.audit_output}")


if __name__ == "__main__":
    main()
