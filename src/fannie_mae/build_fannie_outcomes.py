#!/usr/bin/env python3
"""Construct leakage-safe 3- and 6-month Fannie Mae outcome labels."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import duckdb


def quote(path: Path) -> str:
    return path.as_posix().replace("'", "''")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--panel", required=True, type=Path)
    parser.add_argument("--events", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--report", required=True, type=Path)
    parser.add_argument("--temp-dir", required=True, type=Path)
    parser.add_argument("--threads", type=int, default=4)
    args = parser.parse_args()

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.temp_dir.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect()
    con.execute("SET threads = {}".format(args.threads))
    con.execute("SET temp_directory = '{}'".format(quote(args.temp_dir)))

    panel = quote(args.panel)
    events = quote(args.events)
    output = quote(args.output)
    query = """
    WITH joined AS (
        SELECT
            panel.loan_identifier,
            panel.monthly_reporting_period,
            panel.current_loan_delinquency_status,
            events.zero_balance_code,
            events.zero_balance_effective_date
        FROM read_parquet('{panel}') AS panel
        INNER JOIN read_parquet('{events}') AS events
            USING (loan_identifier, monthly_reporting_period)
    ),
    classified AS (
        SELECT *,
            CASE
                WHEN TRY_CAST(current_loan_delinquency_status AS INTEGER) BETWEEN 0 AND 98
                THEN TRY_CAST(current_loan_delinquency_status AS INTEGER)
                ELSE NULL
            END AS delinquency_bucket,
            CASE WHEN zero_balance_code IS NOT NULL THEN 1 ELSE 0 END AS termination_now
        FROM joined
    ),
    windows AS (
        SELECT *,
            COUNT(*) OVER w3 AS future_month_count_3m,
            COUNT(*) OVER w6 AS future_month_count_6m,
            COALESCE(MAX(CASE WHEN delinquency_bucket BETWEEN 3 AND 98 THEN 1 ELSE 0 END) OVER w3, 0) AS adverse_3m,
            COALESCE(MAX(CASE WHEN delinquency_bucket BETWEEN 3 AND 98 THEN 1 ELSE 0 END) OVER w6, 0) AS adverse_6m,
            COALESCE(MAX(CASE WHEN delinquency_bucket BETWEEN 1 AND 98 THEN 1 ELSE 0 END) OVER w3, 0) AS deterioration_3m,
            COALESCE(MAX(CASE WHEN delinquency_bucket BETWEEN 1 AND 98 THEN 1 ELSE 0 END) OVER w6, 0) AS deterioration_6m,
            COALESCE(MAX(CASE WHEN delinquency_bucket IS NULL THEN 1 ELSE 0 END) OVER w3, 0) AS unknown_3m,
            COALESCE(MAX(CASE WHEN delinquency_bucket IS NULL THEN 1 ELSE 0 END) OVER w6, 0) AS unknown_6m,
            COALESCE(MAX(termination_now) OVER w3, 0) AS termination_3m,
            COALESCE(MAX(termination_now) OVER w6, 0) AS termination_6m
        FROM classified
        WINDOW
            w3 AS (
                PARTITION BY loan_identifier ORDER BY monthly_reporting_period
                RANGE BETWEEN INTERVAL 1 MONTH FOLLOWING AND INTERVAL 3 MONTH FOLLOWING
            ),
            w6 AS (
                PARTITION BY loan_identifier ORDER BY monthly_reporting_period
                RANGE BETWEEN INTERVAL 1 MONTH FOLLOWING AND INTERVAL 6 MONTH FOLLOWING
            )
    )
    SELECT
        loan_identifier,
        monthly_reporting_period,
        current_loan_delinquency_status,
        zero_balance_code,
        zero_balance_effective_date,
        CASE
            WHEN termination_now = 1 OR delinquency_bucket IS NULL OR delinquency_bucket NOT BETWEEN 0 AND 2 THEN NULL
            WHEN adverse_3m = 1 THEN 1
            WHEN termination_3m = 1 OR unknown_3m = 1 OR future_month_count_3m < 3 THEN NULL
            ELSE 0
        END AS formal_adverse_3m,
        CASE
            WHEN termination_now = 1 OR delinquency_bucket IS NULL OR delinquency_bucket NOT BETWEEN 0 AND 2 THEN 'not_at_risk_at_t'
            WHEN adverse_3m = 1 THEN 'event_90plus_dpd'
            WHEN termination_3m = 1 THEN 'censored_termination'
            WHEN unknown_3m = 1 THEN 'censored_unknown_status'
            WHEN future_month_count_3m < 3 THEN 'censored_incomplete_followup'
            ELSE 'observed_no_event'
        END AS formal_adverse_3m_status,
        CASE
            WHEN termination_now = 1 OR delinquency_bucket IS NULL OR delinquency_bucket NOT BETWEEN 0 AND 2 THEN NULL
            WHEN adverse_6m = 1 THEN 1
            WHEN termination_6m = 1 OR unknown_6m = 1 OR future_month_count_6m < 6 THEN NULL
            ELSE 0
        END AS formal_adverse_6m,
        CASE
            WHEN termination_now = 1 OR delinquency_bucket IS NULL OR delinquency_bucket NOT BETWEEN 0 AND 2 THEN 'not_at_risk_at_t'
            WHEN adverse_6m = 1 THEN 'event_90plus_dpd'
            WHEN termination_6m = 1 THEN 'censored_termination'
            WHEN unknown_6m = 1 THEN 'censored_unknown_status'
            WHEN future_month_count_6m < 6 THEN 'censored_incomplete_followup'
            ELSE 'observed_no_event'
        END AS formal_adverse_6m_status,
        CASE
            WHEN termination_now = 1 OR delinquency_bucket IS NULL OR delinquency_bucket != 0 THEN NULL
            WHEN deterioration_3m = 1 THEN 1
            WHEN termination_3m = 1 OR unknown_3m = 1 OR future_month_count_3m < 3 THEN NULL
            ELSE 0
        END AS early_deterioration_3m,
        CASE
            WHEN termination_now = 1 OR delinquency_bucket IS NULL OR delinquency_bucket != 0 THEN 'not_at_risk_at_t'
            WHEN deterioration_3m = 1 THEN 'event_30plus_dpd'
            WHEN termination_3m = 1 THEN 'censored_termination'
            WHEN unknown_3m = 1 THEN 'censored_unknown_status'
            WHEN future_month_count_3m < 3 THEN 'censored_incomplete_followup'
            ELSE 'observed_no_event'
        END AS early_deterioration_3m_status,
        CASE
            WHEN termination_now = 1 OR delinquency_bucket IS NULL OR delinquency_bucket != 0 THEN NULL
            WHEN deterioration_6m = 1 THEN 1
            WHEN termination_6m = 1 OR unknown_6m = 1 OR future_month_count_6m < 6 THEN NULL
            ELSE 0
        END AS early_deterioration_6m,
        CASE
            WHEN termination_now = 1 OR delinquency_bucket IS NULL OR delinquency_bucket != 0 THEN 'not_at_risk_at_t'
            WHEN deterioration_6m = 1 THEN 'event_30plus_dpd'
            WHEN termination_6m = 1 THEN 'censored_termination'
            WHEN unknown_6m = 1 THEN 'censored_unknown_status'
            WHEN future_month_count_6m < 6 THEN 'censored_incomplete_followup'
            ELSE 'observed_no_event'
        END AS early_deterioration_6m_status
    FROM windows
    """.format(panel=panel, events=events)

    con.execute("COPY ({}) TO '{}' (FORMAT PARQUET, COMPRESSION ZSTD)".format(query, output))
    summaries = {}
    label_pairs = [
        ("formal_adverse_3m", "formal_adverse_3m_status"),
        ("formal_adverse_6m", "formal_adverse_6m_status"),
        ("early_deterioration_3m", "early_deterioration_3m_status"),
        ("early_deterioration_6m", "early_deterioration_6m_status"),
    ]
    for label, status in label_pairs:
        aggregate = con.execute(
            "SELECT count(*), count({0}), sum(CASE WHEN {0}=1 THEN 1 ELSE 0 END), "
            "sum(CASE WHEN {0}=0 THEN 1 ELSE 0 END) FROM read_parquet('{1}')".format(label, output)
        ).fetchone()
        reasons = con.execute(
            "SELECT {0}, count(*) FROM read_parquet('{1}') GROUP BY 1 ORDER BY 1".format(status, output)
        ).fetchall()
        summaries[label] = {
            "all_rows": aggregate[0],
            "labelled_rows": aggregate[1],
            "positive_events": aggregate[2],
            "negative_no_event": aggregate[3],
            "status_counts": {key: value for key, value in reasons},
        }
    report = {
        "version": "fannie_outcome_v01",
        "panel_source": args.panel.as_posix(),
        "event_metadata_source": args.events.as_posix(),
        "rows_written": summaries["formal_adverse_3m"]["all_rows"],
        "formal_adverse_definition": "A future interpretable delinquency status from 03 through 98 within the stated horizon; XX and 99 are not events.",
        "early_deterioration_definition": "For loans current at t, a future interpretable delinquency status from 01 through 98 within the stated horizon.",
        "censoring": "Termination, unknown future delinquency status, and incomplete future monthly coverage are censored when no defined event occurs.",
        "label_summaries": summaries,
    }
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    con.close()


if __name__ == "__main__":
    main()
