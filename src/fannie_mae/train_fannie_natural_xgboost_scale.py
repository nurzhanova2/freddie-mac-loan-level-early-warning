#!/usr/bin/env python3
"""Fit one fixed XGBoost model and calibrator without reading OOT data."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.isotonic import IsotonicRegression
from sklearn.metrics import average_precision_score, brier_score_loss, roc_auc_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OrdinalEncoder
from xgboost import XGBClassifier

NUMERIC = ['original_interest_rate','original_upb','original_loan_term','original_loan_to_value_ratio_ltv','original_combined_loan_to_value_ratio_cltv','number_of_borrowers','debt_to_income_dti','borrower_credit_score_at_origination','co_borrower_credit_score_at_origination','mortgage_insurance_percentage','current_interest_rate','current_actual_upb','loan_age','remaining_months_to_legal_maturity','remaining_months_to_maturity']
CATEGORICAL = ['channel','first_time_home_buyer_indicator','loan_purpose','property_type','number_of_units','occupancy_status','property_state','amortization_type','current_loan_delinquency_status','modification_flag']
FEATURES = NUMERIC + CATEGORICAL


def metrics(y: pd.Series, probability) -> dict[str, float]:
    return {
        'roc_auc': round(float(roc_auc_score(y, probability)), 6),
        'pr_auc': round(float(average_precision_score(y, probability)), 6),
        'brier_score': round(float(brier_score_loss(y, probability)), 6),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--target', choices=('formal_adverse_6m', 'early_deterioration_6m'), required=True)
    parser.add_argument('--share', choices=(1, 5, 10, 25), type=int, required=True)
    parser.add_argument('--train-dir', type=Path, default=Path('fannie_mae/data/train_size_sensitivity_v01'))
    parser.add_argument('--validation-dir', type=Path, default=Path('fannie_mae/data/model_samples_v01'))
    parser.add_argument('--output-dir', type=Path, default=Path('fannie_mae/models/train_size_sensitivity_v01'))
    args = parser.parse_args()

    train_path = args.train_dir / f'{args.target}_train_natural_{args.share:02d}pct_v01.parquet'
    validation_path = args.validation_dir / f'{args.target}_validation_sample_v01.parquet'
    output = args.output_dir / args.target / f'{args.share:02d}pct'
    output.mkdir(parents=True, exist_ok=True)

    train = pd.read_parquet(train_path)
    validation = pd.read_parquet(validation_path)
    preprocess = ColumnTransformer([
        ('num', SimpleImputer(strategy='median'), NUMERIC),
        ('cat', Pipeline([
            ('impute', SimpleImputer(strategy='most_frequent')),
            ('ordinal', OrdinalEncoder(handle_unknown='use_encoded_value', unknown_value=-1, encoded_missing_value=-1)),
        ]), CATEGORICAL),
    ])
    estimator = XGBClassifier(
        n_estimators=160, max_depth=6, learning_rate=0.08, min_child_weight=10,
        subsample=0.8, colsample_bytree=0.8, objective='binary:logistic',
        eval_metric='logloss', tree_method='hist', n_jobs=4, random_state=42,
    )
    model = Pipeline([('preprocess', preprocess), ('model', estimator)])
    model.fit(train[FEATURES], train.label)
    validation_raw = model.predict_proba(validation[FEATURES])[:, 1]
    calibrator = IsotonicRegression(out_of_bounds='clip').fit(validation_raw, validation.label)
    validation_calibrated = calibrator.predict(validation_raw)

    joblib.dump(model, output / 'model.joblib')
    joblib.dump(calibrator, output / 'isotonic_calibrator.joblib')
    report = {
        'target': args.target,
        'train_share_pct': args.share,
        'training_data': str(train_path),
        'training_rows': int(len(train)),
        'training_events': int(train.label.sum()),
        'training_event_rate_pct': round(float(train.label.mean() * 100), 6),
        'validation_data': str(validation_path),
        'validation_rows': int(len(validation)),
        'validation_events': int(validation.label.sum()),
        'validation_raw': metrics(validation.label, validation_raw),
        'validation_isotonic_calibrated': metrics(validation.label, validation_calibrated),
        'oot_accessed': False,
        'hyperparameters': estimator.get_params(),
    }
    (output / 'fit_and_calibration_manifest.json').write_text(json.dumps(report, indent=2, default=str) + '\n')


if __name__ == '__main__':
    main()
