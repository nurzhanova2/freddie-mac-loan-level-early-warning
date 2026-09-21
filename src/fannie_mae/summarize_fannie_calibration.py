#!/usr/bin/env python3
from pathlib import Path
import csv,json
base=Path('fannie_mae/reports/models'); out=base/'logistic_isotonic_calibration_v01_summary.csv'; rows=[]
for target in ('formal_adverse_6m','early_deterioration_6m'):
 d=json.loads((base/f'{target}_isotonic_calibration_v01.json').read_text())
 for version,key in [('uncalibrated','out_of_time_test_uncalibrated'),('isotonic_calibrated','out_of_time_test_isotonic_calibrated')]: rows.append({'target':target,'probability_version':version,**d[key]})
with out.open('w',newline='',encoding='utf-8') as h:
 w=csv.DictWriter(h,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
