#!/usr/bin/env python3
"""Fit the interpretable stage-13 logistic baseline on deterministic samples."""
from __future__ import annotations
import argparse, json
from pathlib import Path
import joblib, pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, brier_score_loss, roc_auc_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

NUMERIC = ['original_interest_rate','original_upb','original_loan_term','original_loan_to_value_ratio_ltv','original_combined_loan_to_value_ratio_cltv','number_of_borrowers','debt_to_income_dti','borrower_credit_score_at_origination','co_borrower_credit_score_at_origination','mortgage_insurance_percentage','current_interest_rate','current_actual_upb','loan_age','remaining_months_to_legal_maturity','remaining_months_to_maturity']
CATEGORICAL = ['channel','first_time_home_buyer_indicator','loan_purpose','property_type','number_of_units','occupancy_status','property_state','amortization_type','current_loan_delinquency_status','modification_flag']

def main() -> None:
    p=argparse.ArgumentParser(); p.add_argument('--target', choices=['formal_adverse_6m','early_deterioration_6m'], required=True); p.add_argument('--samples-dir',type=Path,default=Path('fannie_mae/data/model_samples_v01')); p.add_argument('--output-dir',type=Path,default=Path('fannie_mae/models/logistic_v01')); a=p.parse_args(); a.output_dir.mkdir(parents=True,exist_ok=True)
    train=pd.read_parquet(a.samples_dir/f'{a.target}_train_sample_v01.parquet')
    val=pd.read_parquet(a.samples_dir/f'{a.target}_validation_sample_v01.parquet')
    test=pd.read_parquet(a.samples_dir/f'{a.target}_out_of_time_test_sample_v01.parquet')
    pre=ColumnTransformer([('num',Pipeline([('impute',SimpleImputer(strategy='median',add_indicator=True)),('scale',StandardScaler())]),NUMERIC),('cat',Pipeline([('impute',SimpleImputer(strategy='most_frequent')),('onehot',OneHotEncoder(handle_unknown='ignore'))]),CATEGORICAL)])
    model=Pipeline([('preprocess',pre),('model',LogisticRegression(solver='saga',max_iter=120,C=1.0,random_state=42,n_jobs=-1))])
    model.fit(train[NUMERIC+CATEGORICAL],train.label)
    metrics={"target":a.target,"training_sampling":"case-control; probability calibration deferred to stage 14"}
    for name,frame in [('validation',val),('out_of_time_test',test)]:
        prob=model.predict_proba(frame[NUMERIC+CATEGORICAL])[:,1]
        metrics[name]={"rows":int(len(frame)),"events":int(frame.label.sum()),"event_rate_pct":round(float(frame.label.mean()*100),4),"roc_auc":round(float(roc_auc_score(frame.label,prob)),6),"pr_auc":round(float(average_precision_score(frame.label,prob)),6),"brier_uncalibrated":round(float(brier_score_loss(frame.label,prob)),6)}
    joblib.dump(model,a.output_dir/f'{a.target}_logistic_v01.joblib')
    (a.output_dir/f'{a.target}_logistic_metrics_v01.json').write_text(json.dumps(metrics,indent=2)+'\n')

if __name__ == '__main__': main()
