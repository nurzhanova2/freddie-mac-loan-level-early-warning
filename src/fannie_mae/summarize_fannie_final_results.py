#!/usr/bin/env python3
from pathlib import Path
import csv,json
out=Path('fannie_mae/reports/models/final_model_comparison_v01.csv'); out.parent.mkdir(parents=True,exist_ok=True); rows=[]
for model,path in [('logistic',Path('fannie_mae/models/logistic_v01')),('xgboost',Path('fannie_mae/models/xgboost_v01'))]:
 for target in ('formal_adverse_6m','early_deterioration_6m'):
  d=json.loads((path/f'{target}_{model}_metrics_v01.json').read_text())['out_of_time_test']
  rows.append({'model':model,'target':target,'roc_auc':d['roc_auc'],'pr_auc':d['pr_auc'],'out_of_time_event_rate_pct':d['event_rate_pct']})
with out.open('w',newline='',encoding='utf-8') as h:
 w=csv.DictWriter(h,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
