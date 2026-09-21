#!/usr/bin/env python3
"""Train CatBoost or LightGBM on the fixed extended temporal samples."""
from __future__ import annotations
import argparse, json
from pathlib import Path
import joblib, pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.metrics import average_precision_score, brier_score_loss, roc_auc_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OrdinalEncoder
from catboost import CatBoostClassifier
from lightgbm import LGBMClassifier

NUMERIC=['original_interest_rate','original_upb','original_loan_term','original_loan_to_value_ratio_ltv','original_combined_loan_to_value_ratio_cltv','number_of_borrowers','debt_to_income_dti','borrower_credit_score_at_origination','co_borrower_credit_score_at_origination','mortgage_insurance_percentage','current_interest_rate','current_actual_upb','loan_age','remaining_months_to_legal_maturity','remaining_months_to_maturity']
CATEGORICAL=['channel','first_time_home_buyer_indicator','loan_purpose','property_type','number_of_units','occupancy_status','property_state','amortization_type','current_loan_delinquency_status','modification_flag']
FEATURES=NUMERIC+CATEGORICAL
def score(y,p): return {'roc_auc':round(float(roc_auc_score(y,p)),6),'pr_auc':round(float(average_precision_score(y,p)),6),'brier_uncalibrated':round(float(brier_score_loss(y,p)),6)}
def main():
 p=argparse.ArgumentParser(); p.add_argument('--target',choices=['formal_adverse_6m','early_deterioration_6m'],required=True); p.add_argument('--model-type',choices=['catboost','lightgbm'],required=True); p.add_argument('--samples-dir',type=Path,required=True); p.add_argument('--output-dir',type=Path,required=True); a=p.parse_args(); a.output_dir.mkdir(parents=True,exist_ok=True)
 train=pd.read_parquet(a.samples_dir/f'{a.target}_train_sample_v01.parquet'); val=pd.read_parquet(a.samples_dir/f'{a.target}_validation_sample_v01.parquet'); test=pd.read_parquet(a.samples_dir/f'{a.target}_out_of_time_test_sample_v01.parquet')
 pre=ColumnTransformer([('num',SimpleImputer(strategy='median'),NUMERIC),('cat',Pipeline([('impute',SimpleImputer(strategy='most_frequent')),('ordinal',OrdinalEncoder(handle_unknown='use_encoded_value',unknown_value=-1,encoded_missing_value=-1))]),CATEGORICAL)])
 est=CatBoostClassifier(iterations=180,depth=6,learning_rate=0.08,loss_function='Logloss',verbose=False,random_seed=42,thread_count=2) if a.model_type=='catboost' else LGBMClassifier(n_estimators=180,max_depth=6,learning_rate=0.08,min_child_samples=20,subsample=0.8,colsample_bytree=0.8,random_state=42,n_jobs=2,verbosity=-1)
 model=Pipeline([('preprocess',pre),('model',est)]); model.fit(train[FEATURES],train.label)
 report={'target':a.target,'model_type':a.model_type,'training_sampling':'case-control; calibration is fitted on validation only'}
 for name,frame in [('validation',val),('out_of_time_test',test)]: report[name]={'rows':int(len(frame)),'events':int(frame.label.sum()),**score(frame.label,model.predict_proba(frame[FEATURES])[:,1])}
 joblib.dump(model,a.output_dir/f'{a.target}_{a.model_type}_v01.joblib'); (a.output_dir/f'{a.target}_{a.model_type}_metrics_v01.json').write_text(json.dumps(report,indent=2)+'\n')
if __name__=='__main__': main()
