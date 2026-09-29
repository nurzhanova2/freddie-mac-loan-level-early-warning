#!/usr/bin/env python3
"""Summarise validation-only tree hyperparameter selection results."""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


INPUT = Path("fannie_mae/reports/tree_hyperparameter_selection_v01")


def main() -> None:
    tables = [
        pd.read_csv(INPUT / f"{target}_validation_candidates_v01.csv")
        for target in ("formal_adverse_6m", "early_deterioration_6m")
    ]
    candidates = pd.concat(tables, ignore_index=True)
    baseline = candidates.loc[candidates.candidate_id == "fixed_baseline", ["target", "algorithm", "pr_auc"]]
    baseline = baseline.rename(columns={"pr_auc": "fixed_baseline_pr_auc"})
    candidates = candidates.merge(baseline, on=["target", "algorithm"], validate="many_to_one")
    candidates["pr_auc_change_vs_fixed"] = candidates.pr_auc - candidates.fixed_baseline_pr_auc
    candidates = candidates.sort_values(["target", "algorithm", "pr_auc"], ascending=[True, True, False])
    candidates.to_csv(INPUT / "tree_validation_candidate_comparison_v01.csv", index=False)

    # idxmax selects the actual highest PR-AUC row rather than the first row
    # retained by a grouped frame. Candidate IDs are unique within a run.
    per_algorithm = candidates.loc[
        candidates.groupby(["target", "algorithm"])["pr_auc"].idxmax()
    ].sort_values(["target", "algorithm"])
    overall = per_algorithm.loc[
        per_algorithm.groupby("target")["pr_auc"].idxmax()
    ].sort_values("target")
    overall.to_csv(INPUT / "tree_validation_overall_selection_v01.csv", index=False)
    manifest = {
        "version": "tree_hyperparameter_selection_v01",
        "selection_split": "validation",
        "oot_used_for_selection": False,
        "per_algorithm_winners": per_algorithm.to_dict(orient="records"),
        "overall_validation_winners": overall.to_dict(orient="records"),
    }
    (INPUT / "tree_validation_overall_selection_manifest_v01.json").write_text(json.dumps(manifest, indent=2) + "\n")


if __name__ == "__main__":
    main()
