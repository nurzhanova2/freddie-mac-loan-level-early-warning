#!/usr/bin/env python3
"""Produce a local SHAP explanation for the highest-scored OOT alert."""
from __future__ import annotations
import argparse,hashlib
from pathlib import Path
import joblib,matplotlib.pyplot as plt,numpy as np,pandas as pd,xgboost as xgb
from evaluate_fannie_alert_policy import FEATURES
def main():
 p=argparse.ArgumentParser(); p.add_argument('--target',choices=['formal_adverse_6m','early_deterioration_6m'],required=True); p.add_argument('--samples-dir',type=Path,default=Path('fannie_mae/data/model_samples_v01')); p.add_argument('--models-dir',type=Path,default=Path('fannie_mae/models/xgboost_v01')); p.add_argument('--reports-dir',type=Path,default=Path('fannie_mae/reports/models')); p.add_argument('--figures-dir',type=Path,default=Path('fannie_mae/reports/figures/models')); a=p.parse_args(); a.reports_dir.mkdir(parents=True,exist_ok=True);a.figures_dir.mkdir(parents=True,exist_ok=True)
 model=joblib.load(a.models_dir/f'{a.target}_xgboost_v01.joblib');cal=joblib.load(a.models_dir/f'{a.target}_xgboost_isotonic_calibrator_v01.joblib');frame=pd.read_parquet(a.samples_dir/f'{a.target}_out_of_time_test_sample_v01.parquet');frame['risk_score']=cal.predict(model.predict_proba(frame[FEATURES])[:,1]);row=frame.sort_values(['risk_score','loan_identifier'],ascending=[False,True]).iloc[[0]]; X=model.named_steps['preprocess'].transform(row[FEATURES]); names=model.named_steps['preprocess'].get_feature_names_out();values=model.named_steps['model'].get_booster().predict(xgb.DMatrix(X,feature_names=list(names)),pred_contribs=True)[0,:-1]
 case_id=hashlib.sha256(str(row.loan_identifier.iloc[0]).encode()).hexdigest()[:12]
 out=pd.DataFrame({'feature':names,'shap_value':values,'absolute_shap':np.abs(values)}).sort_values('absolute_shap',ascending=False).head(15);out.insert(0,'target',a.target);out.insert(1,'masked_alert_case_id',case_id);out.insert(2,'alert_month',str(row.monthly_reporting_period.iloc[0].date()));out.insert(3,'calibrated_risk_score',float(row.risk_score.iloc[0]));out.to_csv(a.reports_dir/f'{a.target}_xgboost_local_alert_shap_v01.csv',index=False)
 chart=out.sort_values('shap_value');fig,ax=plt.subplots(figsize=(8,5));ax.barh(chart.feature,chart.shap_value,color=np.where(chart.shap_value>=0,'#d62728','#1f77b4'));ax.axvline(0,color='black',linewidth=.8);ax.set(xlabel='SHAP contribution to XGBoost log-odds',title=f'Local explanation: {a.target} highest OOT alert');fig.tight_layout();fig.savefig(a.figures_dir/f'{a.target}_xgboost_local_alert_shap_v01.png',dpi=180);plt.close(fig)
if __name__=='__main__': main()
