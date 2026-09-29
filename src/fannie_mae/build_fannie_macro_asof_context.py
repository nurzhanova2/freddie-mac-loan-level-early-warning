#!/usr/bin/env python3
"""Build a point-in-time macro context table from ALFRED vintage snapshots.

For score month t, every series is requested with vintage_date=t and the
latest observation on or before t is retained. State series are batched only
when every identifier receives the same vintage date: otherwise ALFRED silently
assigns a current vintage to all but the first requested series.
"""
from __future__ import annotations

import argparse
import io
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import urlopen

import pandas as pd


ALFRED_URL = "https://alfred.stlouisfed.org/graph/alfredgraph.csv"
MAX_SERIES_PER_ALFRED_REQUEST = 12
GEOGRAPHIES = (
    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "DC", "FL", "GA", "GU",
    "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", "MA", "MI",
    "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ", "NM", "NY", "NC", "ND",
    "OH", "OK", "OR", "PA", "PR", "RI", "SC", "SD", "TN", "TX", "UT", "VA",
    "VI", "VT", "WA", "WI", "WV", "WY",
)
# Coverage probe at the protocol vintage found no respective ALFRED series.
KNOWN_UNAVAILABLE = {
    "state_unemployment": {"GU", "VI"},
    "state_hpi": {"GU", "PR", "VI"},
}


def month_range(start: str, end: str) -> list[pd.Timestamp]:
    return list(pd.date_range(
        pd.Timestamp(start).to_period("M").to_timestamp(),
        pd.Timestamp(end).to_period("M").to_timestamp(), freq="MS",
    ))


def chunks(items: list[str], size: int) -> list[list[str]]:
    return [items[index:index + size] for index in range(0, len(items), size)]


def fetch_many_as_of(
    series_ids: list[str], vintage_date: pd.Timestamp, timeout_seconds: int, retries: int
) -> dict[str, tuple[pd.Timestamp | None, float | None]]:
    """Fetch one ALFRED snapshot and return one value per series identifier."""
    query = urlencode({
        "id": ",".join(series_ids),
        "vintage_date": ",".join([vintage_date.strftime("%Y-%m-%d")] * len(series_ids)),
    })
    for attempt in range(retries + 1):
        try:
            with urlopen(f"{ALFRED_URL}?{query}", timeout=timeout_seconds) as response:
                frame = pd.read_csv(io.BytesIO(response.read()))
            break
        except HTTPError as error:
            if error.code in {400, 404} or attempt == retries:
                raise RuntimeError(
                    f"ALFRED request failed for {','.join(series_ids)} at {vintage_date:%Y-%m-%d}: {error}"
                ) from error
            time.sleep(min(2**attempt, 8))
        except (URLError, TimeoutError) as error:
            if attempt == retries:
                raise RuntimeError(
                    f"ALFRED request failed for {','.join(series_ids)} at {vintage_date:%Y-%m-%d}: {error}"
                ) from error
            time.sleep(min(2**attempt, 8))

    frame["observation_date"] = pd.to_datetime(frame["observation_date"])
    result: dict[str, tuple[pd.Timestamp | None, float | None]] = {}
    for series_id in series_ids:
        columns = [column for column in frame.columns if column.startswith(f"{series_id}_")]
        if len(columns) != 1:
            raise RuntimeError(f"ALFRED response did not contain exactly one column for {series_id}")
        column = columns[0]
        values = pd.to_numeric(frame[column], errors="coerce")
        admissible = frame.loc[(frame.observation_date <= vintage_date) & values.notna()]
        result[series_id] = (None, None) if admissible.empty else (
            admissible.iloc[-1].observation_date, float(admissible.iloc[-1][column])
        )
    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", default="2021-01")
    parser.add_argument("--end", default="2021-01")
    parser.add_argument("--include-state-series", action="store_true")
    parser.add_argument("--geographies", default=",".join(GEOGRAPHIES))
    parser.add_argument("--sleep-seconds", type=float, default=0.1)
    parser.add_argument("--timeout-seconds", type=int, default=30)
    parser.add_argument("--retries", type=int, default=2)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--checkpoint-every", type=int, default=50)
    parser.add_argument(
        "--output", type=Path,
        default=Path("fannie_mae/data/external/macro_context_asof_v01.csv"),
    )
    return parser.parse_args()


def make_row(
    reporting_month: pd.Timestamp, feature_family: str, geography: str, series_id: str,
    observation_date: pd.Timestamp | None, value: float | None, error: str | None = None,
    request_status: str | None = None,
) -> dict[str, object]:
    return {
        "reporting_month": reporting_month.strftime("%Y-%m"),
        "feature_family": feature_family,
        "geography": geography,
        "series_id": series_id,
        "requested_vintage_date": reporting_month.strftime("%Y-%m-%d"),
        "source_observation_date": observation_date.strftime("%Y-%m-%d") if observation_date is not None else None,
        "value": value,
        "request_error": error,
        "request_status": request_status or ("available" if value is not None else "no_observation"),
        "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
    }


def main() -> None:
    args = parse_args()
    geographies = tuple(item.strip().upper() for item in args.geographies.split(",") if item.strip())
    unknown = sorted(set(geographies) - set(GEOGRAPHIES))
    if unknown:
        raise ValueError(f"Unknown Fannie geographies: {', '.join(unknown)}")
    key_columns = ["reporting_month", "feature_family", "geography", "series_id"]
    prior = pd.DataFrame(columns=key_columns)
    if args.resume and args.output.exists():
        prior = pd.read_csv(args.output)
    if "request_status" not in prior.columns:
        # Legacy output did not distinguish a failed request from a known
        # unavailable series. It is safe to re-request only rows carrying an
        # error in that legacy format.
        prior["request_status"] = prior.get("request_error", pd.Series(index=prior.index, dtype="object")).notna().map({True: "request_failed", False: "available"})
    successful_prior = prior.loc[prior.request_status != "request_failed"]
    completed = set(map(tuple, successful_prior.reindex(columns=key_columns).itertuples(index=False, name=None)))
    rows: list[dict[str, object]] = []

    def persist() -> None:
        if rows:
            result = pd.concat([prior, pd.DataFrame(rows)], ignore_index=True)
            result.drop_duplicates(subset=key_columns, keep="last").to_csv(args.output, index=False)

    def request_group(
        reporting_month: pd.Timestamp, series_spec: dict[str, tuple[str, str]]
    ) -> None:
        pending = {
            series: (feature_family, geography) for series, (feature_family, geography) in series_spec.items()
            if (reporting_month.strftime("%Y-%m"), feature_family, geography, series) not in completed
        }
        if not pending:
            return
        for batch in chunks(list(pending), MAX_SERIES_PER_ALFRED_REQUEST):
            try:
                values = fetch_many_as_of(batch, reporting_month, args.timeout_seconds, args.retries)
                for series in batch:
                    feature_family, geography = pending[series]
                    observation_date, value = values[series]
                    rows.append(make_row(reporting_month, feature_family, geography, series, observation_date, value))
            except RuntimeError as error:
                for series in batch:
                    feature_family, geography = pending[series]
                    rows.append(make_row(
                        reporting_month, feature_family, geography, series, None, None, str(error), "request_failed"
                    ))
            time.sleep(args.sleep_seconds)

    for reporting_month in month_range(args.start, args.end):
        request_group(reporting_month, {
            "FEDFUNDS": ("fedfunds", "US"),
            "UNRATE": ("unemployment", "US"),
        })
        if args.include_state_series:
            request_group(reporting_month, {
                f"{state}UR": ("state_unemployment", state)
                for state in geographies if state not in KNOWN_UNAVAILABLE["state_unemployment"]
            })
            request_group(reporting_month, {
                f"{state}STHPI": ("state_hpi", state)
                for state in geographies if state not in KNOWN_UNAVAILABLE["state_hpi"]
            })
            for family, unavailable in KNOWN_UNAVAILABLE.items():
                for state in sorted(set(geographies) & unavailable):
                    suffix = "UR" if family == "state_unemployment" else "STHPI"
                    series = f"{state}{suffix}"
                    key = (reporting_month.strftime("%Y-%m"), family, state, series)
                    if key not in completed:
                        rows.append(make_row(
                            reporting_month, family, state, series, None, None,
                            "No ALFRED series identified in coverage probe; retained as unavailable.", "unavailable_known",
                        ))
        if len(rows) >= args.checkpoint_every:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            persist()
            prior = pd.concat([prior, pd.DataFrame(rows)], ignore_index=True)
            prior = prior.drop_duplicates(subset=key_columns, keep="last")
            completed.update(map(tuple, pd.DataFrame(rows)[key_columns].itertuples(index=False, name=None)))
            rows.clear()

    result = pd.concat([prior, pd.DataFrame(rows)], ignore_index=True)
    result = result.drop_duplicates(subset=key_columns, keep="last")
    requested = pd.to_datetime(result.requested_vintage_date)
    score_month = pd.to_datetime(result.reporting_month + "-01")
    observation = pd.to_datetime(result.source_observation_date, errors="coerce")
    if (requested > score_month).any() or (observation > score_month).any():
        raise RuntimeError("Point-in-time audit failed: source date after score month.")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(args.output, index=False)
    print(f"Wrote {len(result)} point-in-time macro records to {args.output}")


if __name__ == "__main__":
    main()
