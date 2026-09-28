#!/usr/bin/env python3
"""Build a point-in-time macro context table from ALFRED vintage snapshots.

The script intentionally does not join features to model samples or train a
model.  That requires a separate locked temporal experiment.  Each source is
downloaded at the requested reporting-month vintage, which is stricter than
using a present-day revised FRED download with an arbitrary lag.
"""
from __future__ import annotations

import argparse
import io
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import urlopen

import pandas as pd


ALFRED_URL = "https://alfred.stlouisfed.org/graph/alfredgraph.csv"
STATE_CODES = ("AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "DC", "FL", "GA", "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ", "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY")


def fetch_as_of(series_id: str, vintage_date: pd.Timestamp) -> tuple[pd.Timestamp, float] | tuple[None, None]:
    query = urlencode({"id": series_id, "vintage_date": vintage_date.strftime("%Y-%m-%d")})
    with urlopen(f"{ALFRED_URL}?{query}", timeout=30) as response:
        frame = pd.read_csv(io.BytesIO(response.read()))
    value_column = frame.columns[-1]
    frame["observation_date"] = pd.to_datetime(frame["observation_date"])
    frame[value_column] = pd.to_numeric(frame[value_column], errors="coerce")
    admissible = frame.loc[(frame.observation_date <= vintage_date) & frame[value_column].notna()]
    if admissible.empty:
        return None, None
    latest = admissible.iloc[-1]
    return latest.observation_date, float(latest[value_column])


def month_range(start: str, end: str) -> list[pd.Timestamp]:
    return list(pd.date_range(pd.Timestamp(start).to_period("M").to_timestamp(), pd.Timestamp(end).to_period("M").to_timestamp(), freq="MS"))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", default="2021-01")
    parser.add_argument("--end", default="2021-01")
    parser.add_argument("--include-state-series", action="store_true")
    parser.add_argument("--sleep-seconds", type=float, default=0.1)
    parser.add_argument("--output", type=Path, default=Path("fannie_mae/data/external/macro_context_asof_v01.csv"))
    args = parser.parse_args()
    rows: list[dict[str, object]] = []
    for reporting_month in month_range(args.start, args.end):
        series = [("fedfunds", "US", "FEDFUNDS"), ("unemployment", "US", "UNRATE")]
        if args.include_state_series:
            series += [("state_unemployment", state, f"{state}UR") for state in STATE_CODES]
            series += [("state_hpi", state, f"{state}STHPI") for state in STATE_CODES]
        for feature_family, geography, series_id in series:
            observation_date, value = fetch_as_of(series_id, reporting_month)
            rows.append({
                "reporting_month": reporting_month.strftime("%Y-%m"),
                "feature_family": feature_family,
                "geography": geography,
                "series_id": series_id,
                "requested_vintage_date": reporting_month.strftime("%Y-%m-%d"),
                "source_observation_date": observation_date.strftime("%Y-%m-%d") if observation_date is not None else None,
                "value": value,
                "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
            })
            time.sleep(args.sleep_seconds)
    result = pd.DataFrame(rows)
    if (pd.to_datetime(result.requested_vintage_date) > pd.to_datetime(result.reporting_month + "-01")).any():
        raise RuntimeError("A macro source was requested after its score month")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(args.output, index=False)
    print(f"Wrote {len(result)} point-in-time macro records to {args.output}")


if __name__ == "__main__":
    main()
