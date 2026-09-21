#!/usr/bin/env python3
"""Calibrate a stage-13 case-control model on validation only."""
from __future__ import annotations
import argparse, json
from pathlib import Path
import joblib, matplotlib.pyplot as plt, pandas as pd
from sklearn.calibration import calibration_curve
from sklearn.isotonic import IsotonicRegression
from sklearn.metrics import average_precision_score, brier_score_loss, roc_auc_score

FEATURES=['original_interest_rate','original_upb','original_loan_term','original_loan_to_value_ratio_ltv','original_combined_loan_to_value_ratio_cltv','number_of_borrowers','debt_to_income_dti','borrower_credit_score_at_origination','co_borrower_credit_score_at_origination','mortgage_insurance_percentage','current_interest_rate','current_actual_upb','loan_age','remaining_months_to_legal_maturity','remaining_months_to_maturity','channel','first_time_home_buyer_indicator','loan_purpose','property_type','number_of_units','occupancy_status','property_state','amortization_type','current_loan_delinquency_status','modification_flag']
def scores(y,p): return {'roc_auc':round(float(roc_auc_score(y,p)),6),'pr_auc':round(float(average_precision_score(y,p)),6),'brier_score':round(float(brier_score_loss(y,p)),6)}
def main():
 p=argparse.ArgumentParser(); p.add_argument('--target',choices=['formal_adverse_6m','early_deterioration_6m'],required=True); p.add_argument('--model-type',choices=['logistic','xgboost','catboost','lightgbm'],default='logistic'); p.add_argument('--samples-dir',type=Path,default=Path('fannie_mae/data/model_samples_v01')); p.add_argument('--models-dir',type=Path); p.add_argument('--reports-dir',type=Path,default=Path('fannie_mae/reports/models')); p.add_argument('--figures-dir',type=Path,default=Path('fannie_mae/reports/figures/models')); a=p.parse_args(); a.reports_dir.mkdir(parents=True,exist_ok=True); a.figures_dir.mkdir(parents=True,exist_ok=True)
 models_dir=a.models_dir or Path(f'fannie_mae/models/{a.model_type}_v01')
 model=joblib.load(models_dir/f'{a.target}_{a.model_type}_v01.joblib')
 val=pd.read_parquet(a.samples_dir/f'{a.target}_validation_sample_v01.parquet'); test=pd.read_parquet(a.samples_dir/f'{a.target}_out_of_time_test_sample_v01.parquet')
 val_raw=model.predict_proba(val[FEATURES])[:,1]; test_raw=model.predict_proba(test[FEATURES])[:,1]
 calibrator=IsotonicRegression(out_of_bounds='clip').fit(val_raw,val.label)
 test_cal=calibrator.predict(test_raw)
 joblib.dump(calibrator,models_dir/f'{a.target}_{a.model_type}_isotonic_calibrator_v01.joblib')
 payload={'target':a.target,'model_type':a.model_type,'calibration_data':'validation natural-rate deterministic 1% sample only','evaluation_data':'out_of_time_test natural-rate deterministic 1% sample','validation_rows':int(len(val)),'validation_events':int(val.label.sum()),'out_of_time_test_rows':int(len(test)),'out_of_time_test_events':int(test.label.sum()),'out_of_time_test_uncalibrated':scores(test.label,test_raw),'out_of_time_test_isotonic_calibrated':scores(test.label,test_cal)}
 (a.reports_dir/f'{a.target}_{a.model_type}_isotonic_calibration_v01.json').write_text(json.dumps(payload,indent=2)+'\n')
 plt.style.use('seaborn-v0_8-whitegrid'); fig,ax=plt.subplots(figsize=(6,6))
 for prob,label,colour in [(test_raw,'Uncalibrated','#d62728'),(test_cal,'Isotonic calibrated','#1f77b4')]:
  observed,predicted=calibration_curve(test.label,prob,n_bins=10,strategy='quantile')
  ax.plot(predicted,observed,marker='o',label=label,color=colour)
 ax.plot([0,1],[0,1],'k--',label='Perfect calibration'); ax.set(xlabel='Mean predicted probability',ylabel='Observed event frequency',title=f'Reliability diagram: {a.target} ({a.model_type})'); ax.legend(); fig.tight_layout(); fig.savefig(a.figures_dir/f'{a.target}_{a.model_type}_calibration_v01.png',dpi=180); plt.close(fig)
if __name__=='__main__': main()
