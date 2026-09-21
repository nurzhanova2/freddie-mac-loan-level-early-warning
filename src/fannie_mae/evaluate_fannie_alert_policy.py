#!/usr/bin/env python3
"""Evaluate calibrated XGBoost alert capacity on out-of-time data."""
from __future__ import annotations
import argparse,csv,json
from pathlib import Path
import joblib,matplotlib.pyplot as plt,pandas as pd

FEATURES=['original_interest_rate','original_upb','original_loan_term','original_loan_to_value_ratio_ltv','original_combined_loan_to_value_ratio_cltv','number_of_borrowers','debt_to_income_dti','borrower_credit_score_at_origination','co_borrower_credit_score_at_origination','mortgage_insurance_percentage','current_interest_rate','current_actual_upb','loan_age','remaining_months_to_legal_maturity','remaining_months_to_maturity','channel','first_time_home_buyer_indicator','loan_purpose','property_type','number_of_units','occupancy_status','property_state','amortization_type','current_loan_delinquency_status','modification_flag']
def main():
 p=argparse.ArgumentParser(); p.add_argument('--target',choices=['formal_adverse_6m','early_deterioration_6m'],required=True); p.add_argument('--samples-dir',type=Path,default=Path('fannie_mae/data/model_samples_v01')); p.add_argument('--models-dir',type=Path,default=Path('fannie_mae/models/xgboost_v01')); p.add_argument('--reports-dir',type=Path,default=Path('fannie_mae/reports/models')); p.add_argument('--figures-dir',type=Path,default=Path('fannie_mae/reports/figures/models')); a=p.parse_args(); a.reports_dir.mkdir(parents=True,exist_ok=True); a.figures_dir.mkdir(parents=True,exist_ok=True)
 test=pd.read_parquet(a.samples_dir/f'{a.target}_out_of_time_test_sample_v01.parquet')
 model=joblib.load(a.models_dir/f'{a.target}_xgboost_v01.joblib'); calibrator=joblib.load(a.models_dir/f'{a.target}_xgboost_isotonic_calibrator_v01.joblib')
 test['score']=calibrator.predict(model.predict_proba(test[FEATURES])[:,1])
 test=test.sort_values(['score','loan_identifier','monthly_reporting_period'],ascending=[False,True,True],kind='mergesort').reset_index(drop=True)
 rows=[]
 for capacity in (0.01,0.05,0.10):
  alerts=max(1,round(len(test)*capacity)); selected=test.iloc[:alerts]; tp=int(selected.label.sum()); fp=alerts-tp; total_events=int(test.label.sum())
  rows.append({'target':a.target,'alert_capacity_pct':capacity*100,'alert_count':alerts,'threshold_score':float(selected.score.iloc[-1]),'true_positives':tp,'false_positives':fp,'false_negatives':total_events-tp,'precision_pct':100*tp/alerts,'recall_pct':100*tp/total_events,'false_alerts_per_true_positive':fp/tp if tp else None})
 out=a.reports_dir/f'{a.target}_xgboost_alert_policy_v01.csv'; pd.DataFrame(rows).to_csv(out,index=False)
 plt.style.use('seaborn-v0_8-whitegrid'); fig,ax=plt.subplots(figsize=(7,4.5)); frame=pd.DataFrame(rows); ax.plot(frame.alert_capacity_pct,frame.precision_pct,marker='o',label='Precision'); ax.plot(frame.alert_capacity_pct,frame.recall_pct,marker='o',label='Recall'); ax.set(xlabel='Alert capacity, % of out-of-time observations',ylabel='Metric, %',title=f'Alert-capacity policy: {a.target}'); ax.legend(); fig.tight_layout(); fig.savefig(a.figures_dir/f'{a.target}_xgboost_alert_policy_v01.png',dpi=180); plt.close(fig)
if __name__=='__main__': main()
