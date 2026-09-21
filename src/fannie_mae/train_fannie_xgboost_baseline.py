#!/usr/bin/env python3
"""CPU XGBoost comparator on the fixed stage-13 samples."""
from __future__ import annotations
import argparse
import json
from pathlib import Path

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.metrics import average_precision_score, brier_score_loss, roc_auc_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OrdinalEncoder
from xgboost import XGBClassifier

NUMERIC = ['original_interest_rate','original_upb','original_loan_term','original_loan_to_value_ratio_ltv','original_combined_loan_to_value_ratio_cltv','number_of_borrowers','debt_to_income_dti','borrower_credit_score_at_origination','co_borrower_credit_score_at_origination','mortgage_insurance_percentage','current_interest_rate','current_actual_upb','loan_age','remaining_months_to_legal_maturity','remaining_months_to_maturity']
CATEGORICAL = ['channel','first_time_home_buyer_indicator','loan_purpose','property_type','number_of_units','occupancy_status','property_state','amortization_type','current_loan_delinquency_status','modification_flag']
FEATURES = NUMERIC + CATEGORICAL

def metrics(y, probability):
    return {'roc_auc': round(float(roc_auc_score(y, probability)), 6), 'pr_auc': round(float(average_precision_score(y, probability)), 6), 'brier_uncalibrated': round(float(brier_score_loss(y, probability)), 6)}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--target', choices=['formal_adverse_6m','early_deterioration_6m'], required=True)
    parser.add_argument('--samples-dir', type=Path, default=Path('fannie_mae/data/model_samples_v01'))
    parser.add_argument('--output-dir', type=Path, default=Path('fannie_mae/models/xgboost_v01'))
    args = parser.parse_args(); args.output_dir.mkdir(parents=True, exist_ok=True)
    train = pd.read_parquet(args.samples_dir / f'{args.target}_train_sample_v01.parquet')
    validation = pd.read_parquet(args.samples_dir / f'{args.target}_validation_sample_v01.parquet')
    test = pd.read_parquet(args.samples_dir / f'{args.target}_out_of_time_test_sample_v01.parquet')
    preprocess = ColumnTransformer([('num', SimpleImputer(strategy='median'), NUMERIC), ('cat', Pipeline([('impute',SimpleImputer(strategy='most_frequent')), ('ordinal',OrdinalEncoder(handle_unknown='use_encoded_value',unknown_value=-1,encoded_missing_value=-1))]), CATEGORICAL)])
    estimator = XGBClassifier(n_estimators=160,max_depth=6,learning_rate=0.08,min_child_weight=10,subsample=0.8,colsample_bytree=0.8,objective='binary:logistic',eval_metric='logloss',tree_method='hist',n_jobs=4,random_state=42)
    model = Pipeline([('preprocess', preprocess), ('model', estimator)])
    model.fit(train[FEATURES], train.label)
    report = {'target': args.target, 'training_sampling': 'case-control; probability calibration deferred until model comparison is complete'}
    for name, frame in [('validation', validation), ('out_of_time_test', test)]:
        probability = model.predict_proba(frame[FEATURES])[:, 1]
        report[name] = {'rows': int(len(frame)), 'events': int(frame.label.sum()), 'event_rate_pct': round(float(frame.label.mean()*100),4), **metrics(frame.label, probability)}
    joblib.dump(model, args.output_dir / f'{args.target}_xgboost_v01.joblib')
    (args.output_dir / f'{args.target}_xgboost_metrics_v01.json').write_text(json.dumps(report, indent=2)+'\n')

if __name__ == '__main__':
    main()
