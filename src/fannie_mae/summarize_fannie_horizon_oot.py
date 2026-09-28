#!/usr/bin/env python3
"""Derive prevalence-adjusted horizon-comparison metrics from frozen OOT results."""
from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--reports-dir", type=Path, default=Path("fannie_mae/reports/horizon_sensitivity_v01"))
    parser.add_argument("--figures-dir", type=Path, default=Path("fannie_mae/reports/figures/horizon_sensitivity_v01"))
    args = parser.parse_args()
    metrics = pd.read_csv(args.reports_dir / "horizon_oot_metrics_summary_v01.csv")
    prevalence = metrics.oot_event_rate_pct / 100
    metrics["pr_auc_lift"] = metrics.pr_auc_raw / prevalence
    metrics["trigger_precision_lift"] = (metrics.trigger_precision_pct / 100) / prevalence
    metrics["null_brier"] = prevalence * (1 - prevalence)
    metrics["brier_skill_score"] = 1 - metrics.brier_calibrated / metrics.null_brier
    metrics.to_csv(args.reports_dir / "horizon_oot_comparability_summary_v01.csv", index=False)
    args.figures_dir.mkdir(parents=True, exist_ok=True)
    for outcome, frame in metrics.groupby("outcome_family", sort=True):
        frame = frame.sort_values("horizon_months")
        fig, axes = plt.subplots(2, 2, figsize=(11, 7.5))
        for axis, (column, label) in zip(axes.flat, [
            ("roc_auc_raw", "ROC-AUC"), ("pr_auc_lift", "PR-AUC / event rate"),
            ("brier_skill_score", "Brier skill score"), ("trigger_precision_lift", "Queue precision / event rate"),
        ]):
            axis.plot(frame.horizon_months, frame[column], marker="o", linewidth=2, color="#15375d")
            axis.set(xlabel="Prediction horizon, months", ylabel=label)
            axis.set_xticks([3, 6, 12])
            axis.grid(alpha=0.25)
        fig.suptitle(f"Prevalence-adjusted common-OOT comparison: {outcome}")
        fig.tight_layout()
        fig.savefig(args.figures_dir / f"{outcome}_horizon_oot_comparability_v01.png", dpi=180)
        plt.close(fig)


if __name__ == "__main__":
    main()
