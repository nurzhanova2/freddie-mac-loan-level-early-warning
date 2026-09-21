#!/usr/bin/env python3
"""Evaluate pre-specified calibrated XGBoost/CatBoost probability ensembles."""
from __future__ import annotations
import argparse
from pathlib import Path
import joblib, numpy as np, pandas as pd
from sklearn.isotonic import IsotonicRegression
from sklearn.metrics import average_precision_score, brier_score_loss, roc_auc_score

NUMERIC=['original_interest_rate','original_upb','original_loan_term','original_loan_to_value_ratio_ltv','original_combined_loan_to_value_ratio_cltv','number_of_borrowers','debt_to_income_dti','borrower_credit_score_at_origination','co_borrower_credit_score_at_origination','mortgage_insurance_percentage','current_interest_rate','current_actual_upb','loan_age','remaining_months_to_legal_maturity','remaining_months_to_maturity']
CATEGORICAL=['channel','first_time_home_buyer_indicator','loan_purpose','property_type','number_of_units','occupancy_status','property_state','amortization_type','current_loan_delinquency_status','modification_flag']
FEATURES=NUMERIC+CATEGORICAL
def pred(model, f):
 return np.concatenate([model.predict_proba(f.iloc[i:i+100000][FEATURES])[:,1] for i in range(0,len(f),100000)])
def metrics(y,p,cap):
 row={'roc_auc':roc_auc_score(y,p),'pr_auc':average_precision_score(y,p),'brier':brier_score_loss(y,p)}
 n=max(1,round(len(y)*cap)); top=np.argsort(-p,kind='stable')[:n]; tp=int(np.asarray(y)[top].sum()); row.update(precision_pct=100*tp/n,recall_pct=100*tp/int(y.sum()))
 return row
def main():
 p=argparse.ArgumentParser();p.add_argument('--target',choices=['formal_adverse_6m','early_deterioration_6m'],required=True);p.add_argument('--samples-dir',type=Path,default=Path('fannie_mae/data/model_samples_v02_q1q3'));p.add_argument('--models-root',type=Path,default=Path('fannie_mae/models_v02_q1q3'));p.add_argument('--out',type=Path,default=Path('fannie_mae/reports/models_v02_q1q3'));a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True)
 val=pd.read_parquet(a.samples_dir/f'{a.target}_validation_sample_v01.parquet'); test=pd.read_parquet(a.samples_dir/f'{a.target}_out_of_time_test_sample_v01.parquet')
 xgb=joblib.load(a.models_root/'xgboost'/f'{a.target}_xgboost_v01.joblib'); cat=joblib.load(a.models_root/'catboost'/f'{a.target}_catboost_v01.joblib')
 xv,cv,xt,ct=pred(xgb,val),pred(cat,val),pred(xgb,test),pred(cat,test); cap=.01 if a.target=='formal_adverse_6m' else .05; rows=[]
 for weight in (0.25,0.50,0.75):
  cal=IsotonicRegression(out_of_bounds='clip').fit(weight*xv+(1-weight)*cv,val.label); vp=cal.predict(weight*xv+(1-weight)*cv); tp=cal.predict(weight*xt+(1-weight)*ct)
  rows.append({'target':a.target,'xgboost_weight':weight,'selection':'pre_specified','validation_pr_auc':average_precision_score(val.label,vp),**{f'oot_{k}':v for k,v in metrics(test.label,tp,cap).items()}})
 pd.DataFrame(rows).to_csv(a.out/f'{a.target}_hybrid_ensemble_v01.csv',index=False)
if __name__=='__main__':main()
