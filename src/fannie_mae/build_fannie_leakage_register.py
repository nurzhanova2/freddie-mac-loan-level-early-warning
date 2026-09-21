#!/usr/bin/env python3
"""Create an auditable initial feature-eligibility register from the Fannie dictionary."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

IDENTIFIERS = {"reference_pool_id", "loan_identifier"}
TIME_INDEX = {"monthly_reporting_period"}
CURRENT_CONTEXT = {
    "current_interest_rate", "current_actual_upb", "loan_age",
    "remaining_months_to_legal_maturity", "remaining_months_to_maturity",
    "current_loan_delinquency_status", "loan_payment_history", "modification_flag",
}
OUTCOME_OR_POST_EVENT_POSITIONS = set(range(43, 73))
WORKOUT_OR_RESOLUTION_FIELDS = {
    "servicing_activity_indicator", "borrower_assistance_plan",
    "alternative_delinquency_resolution",
    "alternative_delinquency_resolution_count", "total_deferral_amount",
    "payment_deferral_modification_event_indicator",
    "repurchase_make_whole_proceeds_flag",
}


def policy(row: dict[str, str]) -> tuple[str, str, str]:
    position = int(row["field_position"])
    name = row["field_name"]
    if name in IDENTIFIERS:
        return "exclude_identifier", "not a predictor", "Identifier; retained only for joins and panel keys."
    if name in TIME_INDEX:
        return "index_only", "at observation month", "Time index; retained for temporal split and label alignment."
    if position <= 39:
        return "candidate_feature", "origination or known at observation", "Static origination characteristic; fit transformations on training data only."
    if name in CURRENT_CONTEXT:
        if name == "loan_payment_history":
            return "candidate_feature_conditional", "history through observation month only", "Use only trailing history known at time t; validate parser before modelling."
        return "candidate_feature", "at observation month", "Current or historical context available at the prediction date."
    if position in OUTCOME_OR_POST_EVENT_POSITIONS:
        return "label_only_or_exclude", "after or at termination", "Potential termination, foreclosure, disposition, recovery or settlement information; excluded from model features."
    if name in WORKOUT_OR_RESOLUTION_FIELDS:
        return "exclude_initial_model", "may follow deterioration", "Workout or resolution information; excluded from the initial early-warning model pending a separate intervention analysis."
    return "exclude_pending_review", "not established for initial panel", "Outside the v01 base feature set; requires explicit temporal-availability review before use."


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dictionary", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    with args.dictionary.open(newline="", encoding="utf-8") as source:
        rows = list(csv.DictReader(source))
    if len(rows) != 113:
        raise ValueError("Expected 113 raw-field records, found {}.".format(len(rows)))
    names = [
        "field_position", "field_name", "official_field_name",
        "sf_loan_performance_applicability", "type", "availability_assessment",
        "v01_usage_decision", "rationale",
    ]
    output = []
    for row in rows:
        decision, availability, rationale = policy(row)
        output.append({
            "field_position": row["field_position"],
            "field_name": row["field_name"],
            "official_field_name": row["official_field_name"],
            "sf_loan_performance_applicability": row["sf_loan_performance_applicability"],
            "type": row["type"],
            "availability_assessment": availability,
            "v01_usage_decision": decision,
            "rationale": rationale,
        })
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as target:
        writer = csv.DictWriter(target, fieldnames=names)
        writer.writeheader()
        writer.writerows(output)


if __name__ == "__main__":
    main()

