#!/usr/bin/env python3
"""Combine stage-13 logistic metrics into one citation-ready table."""
from __future__ import annotations
import csv, json
from pathlib import Path

root=Path('fannie_mae/models/logistic_v01')
output=Path('fannie_mae/reports/models/logistic_baseline_v01_summary.csv')
output.parent.mkdir(parents=True, exist_ok=True)
rows=[]
for target in ('formal_adverse_6m','early_deterioration_6m'):
    payload=json.loads((root/f'{target}_logistic_metrics_v01.json').read_text())
    for split in ('validation','out_of_time_test'):
        item=payload[split]
        rows.append({'model':'regularized_logistic_regression_v01','target':target,'split':split,**item,'probability_status':'uncalibrated_case_control_training'})
with output.open('w',newline='',encoding='utf-8') as handle:
    writer=csv.DictWriter(handle,fieldnames=list(rows[0]))
    writer.writeheader(); writer.writerows(rows)
