#!/usr/bin/env python3
"""Estimate time from selected out-of-time alerts to their observed event."""
from __future__ import annotations
import argparse
from pathlib import Path
import duckdb,joblib,pandas as pd
from evaluate_fannie_alert_policy import FEATURES
COHORTS=('2006Q1','2008Q1','2012Q1','2016Q1','2020Q1','2022Q1','2024Q1')
def main():
 p=argparse.ArgumentParser(); p.add_argument('--target',choices=['formal_adverse_6m','early_deterioration_6m'],required=True); p.add_argument('--capacity',type=float,required=True); p.add_argument('--samples-dir',type=Path,default=Path('fannie_mae/data/model_samples_v01')); p.add_argument('--models-dir',type=Path,default=Path('fannie_mae/models/xgboost_v01')); p.add_argument('--processed-dir',type=Path,default=Path('fannie_mae/data/processed')); p.add_argument('--out',type=Path,default=Path('fannie_mae/reports/models')); a=p.parse_args(); a.out.mkdir(parents=True,exist_ok=True)
 test=pd.read_parquet(a.samples_dir/f'{a.target}_out_of_time_test_sample_v01.parquet'); model=joblib.load(a.models_dir/f'{a.target}_xgboost_v01.joblib'); cal=joblib.load(a.models_dir/f'{a.target}_xgboost_isotonic_calibrator_v01.joblib')
 test['score']=cal.predict(model.predict_proba(test[FEATURES])[:,1]); test=test.sort_values(['score','loan_identifier','monthly_reporting_period'],ascending=[False,True,True],kind='mergesort'); selected=test.iloc[:round(len(test)*a.capacity)]; selected=selected[selected.label==1][['loan_identifier','monthly_reporting_period','acquisition_cohort']]
 sel=a.out/f'_lead_time_{a.target}.parquet'; selected.to_parquet(sel,index=False)
 paths='['+', '.join(repr(str(a.processed_dir/f'{c}_monthly_panel_base.parquet')) for c in COHORTS)+']'; condition="try_cast(p.current_loan_delinquency_status AS INTEGER) BETWEEN 3 AND 98" if a.target=='formal_adverse_6m' else "try_cast(p.current_loan_delinquency_status AS INTEGER) BETWEEN 1 AND 98"
 con=duckdb.connect(); q=f"""WITH panel AS (SELECT *,regexp_extract(filename,'([0-9]{{4}}Q[1-4])_',1) AS acquisition_cohort FROM read_parquet({paths},filename=true)), hit AS (SELECT s.loan_identifier,s.monthly_reporting_period AS alert_month,min(date_diff('month',s.monthly_reporting_period,p.monthly_reporting_period)) AS months_to_event FROM read_parquet({repr(str(sel))}) s JOIN panel p USING(acquisition_cohort,loan_identifier) WHERE p.monthly_reporting_period>s.monthly_reporting_period AND p.monthly_reporting_period<=s.monthly_reporting_period+INTERVAL 6 MONTH AND {condition} GROUP BY 1,2) SELECT count(*) AS alerted_events_with_observed_event,round(avg(months_to_event),3) AS mean_months_to_event,quantile_cont(months_to_event,0.5) AS median_months_to_event,min(months_to_event) AS min_months_to_event,max(months_to_event) AS max_months_to_event FROM hit"""
 out=con.execute(q).fetchdf(); out.insert(0,'target',a.target); out.insert(1,'capacity_pct',a.capacity*100); out.to_csv(a.out/f'{a.target}_trigger_lead_time_v01.csv',index=False)
 sel.unlink()
if __name__=='__main__': main()
