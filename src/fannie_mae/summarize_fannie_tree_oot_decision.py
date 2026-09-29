#!/usr/bin/env python3
"""Record the governance decision after the locked tree-model OOT evaluation."""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


ROOT = Path("fannie_mae/reports/tree_hyperparameter_selection_v01")


def row(frame: pd.DataFrame, key: str) -> pd.Series:
    return frame.loc[frame.model_key == key].iloc[0]


def main() -> None:
    metrics = pd.read_csv(ROOT / "tree_oot_calibrated_comparison_v01.csv")
    formal = metrics.loc[metrics.target == "formal_adverse_6m"]
    early = metrics.loc[metrics.target == "early_deterioration_6m"]
    selected_formal = row(formal, "lightgbm_medium_regularised")
    fixed_light = row(formal, "lightgbm_fixed_baseline")
    fixed_xgb_formal = row(formal, "xgboost_fixed_baseline")
    fixed_xgb_early = row(early, "xgboost_fixed_baseline")
    cat_early = row(early, "catboost_fixed_baseline")

    formal_rule_passed = (
        selected_formal.pr_auc_raw > fixed_light.pr_auc_raw
        and selected_formal.brier_calibrated < fixed_light.brier_calibrated
        and selected_formal.trigger_precision_pct >= fixed_xgb_formal.trigger_precision_pct
        and selected_formal.mean_lead_time_months >= fixed_xgb_formal.mean_lead_time_months
    )
    records = [
        {
            "target": "formal_adverse_6m",
            "validation_selected_configuration": "lightgbm_medium_regularised",
            "oot_governance_reference": "xgboost_fixed_baseline",
            "decision": "retain_xgboost_fixed_baseline",
            "decision_rule_passed": bool(formal_rule_passed),
            "selected_oot_pr_auc_raw": selected_formal.pr_auc_raw,
            "reference_oot_pr_auc_raw": fixed_xgb_formal.pr_auc_raw,
            "selected_brier_calibrated": selected_formal.brier_calibrated,
            "reference_brier_calibrated": fixed_xgb_formal.brier_calibrated,
            "selected_trigger_precision_pct": selected_formal.trigger_precision_pct,
            "reference_trigger_precision_pct": fixed_xgb_formal.trigger_precision_pct,
            "selected_mean_lead_time_months": selected_formal.mean_lead_time_months,
            "reference_mean_lead_time_months": fixed_xgb_formal.mean_lead_time_months,
            "rationale": "Validation-selected LightGBM does not satisfy the pre-specified OOT update rule.",
        },
        {
            "target": "early_deterioration_6m",
            "validation_selected_configuration": "xgboost_fixed_baseline",
            "oot_governance_reference": "xgboost_fixed_baseline",
            "decision": "retain_xgboost_fixed_baseline",
            "decision_rule_passed": True,
            "selected_oot_pr_auc_raw": fixed_xgb_early.pr_auc_raw,
            "reference_oot_pr_auc_raw": fixed_xgb_early.pr_auc_raw,
            "selected_brier_calibrated": fixed_xgb_early.brier_calibrated,
            "reference_brier_calibrated": fixed_xgb_early.brier_calibrated,
            "selected_trigger_precision_pct": fixed_xgb_early.trigger_precision_pct,
            "reference_trigger_precision_pct": fixed_xgb_early.trigger_precision_pct,
            "selected_mean_lead_time_months": fixed_xgb_early.mean_lead_time_months,
            "reference_mean_lead_time_months": fixed_xgb_early.mean_lead_time_months,
            "rationale": (
                "Fixed XGBoost was selected before OOT. CatBoost OOT differences are recorded as an exploratory "
                "future candidate and do not justify post-test model selection."
            ),
            "catboost_oot_pr_auc_calibrated": cat_early.pr_auc_calibrated,
            "catboost_brier_calibrated": cat_early.brier_calibrated,
            "catboost_trigger_precision_pct": cat_early.trigger_precision_pct,
            "catboost_mean_lead_time_months": cat_early.mean_lead_time_months,
        },
    ]
    table = pd.DataFrame(records)
    table.to_csv(ROOT / "tree_oot_governance_decision_v01.csv", index=False)
    (ROOT / "tree_oot_governance_decision_manifest_v01.json").write_text(json.dumps({
        "version": "tree_oot_governance_decision_v01",
        "prototype_update": "no",
        "active_model_policy": "retain_frozen_xgboost_v01_pending_separate_xai_and_export_audit",
        "records": records,
    }, indent=2, default=lambda value: value.item() if hasattr(value, "item") else str(value)) + "\n")


if __name__ == "__main__":
    main()
