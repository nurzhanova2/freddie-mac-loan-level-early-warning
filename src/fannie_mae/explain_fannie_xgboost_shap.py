#!/usr/bin/env python3
"""Initial global SHAP audit of the leading XGBoost model."""
from __future__ import annotations
import argparse
from pathlib import Path
import joblib,matplotlib.pyplot as plt,numpy as np,pandas as pd,xgboost as xgb
from evaluate_fannie_alert_policy import FEATURES
def main():
 p=argparse.ArgumentParser(); p.add_argument('--target',choices=['formal_adverse_6m','early_deterioration_6m'],required=True); p.add_argument('--sample-size',type=int,default=5000); p.add_argument('--samples-dir',type=Path,default=Path('fannie_mae/data/model_samples_v01')); p.add_argument('--models-dir',type=Path,default=Path('fannie_mae/models/xgboost_v01')); p.add_argument('--reports-dir',type=Path,default=Path('fannie_mae/reports/models')); p.add_argument('--figures-dir',type=Path,default=Path('fannie_mae/reports/figures/models')); a=p.parse_args(); a.reports_dir.mkdir(parents=True,exist_ok=True); a.figures_dir.mkdir(parents=True,exist_ok=True)
 model=joblib.load(a.models_dir/f'{a.target}_xgboost_v01.joblib'); frame=pd.read_parquet(a.samples_dir/f'{a.target}_out_of_time_test_sample_v01.parquet').sample(n=a.sample_size,random_state=42)
 X=model.named_steps['preprocess'].transform(frame[FEATURES]); names=model.named_steps['preprocess'].get_feature_names_out(); values=model.named_steps['model'].get_booster().predict(xgb.DMatrix(X, feature_names=list(names)), pred_contribs=True)[:, :-1]
 importance=pd.DataFrame({'feature':names,'mean_abs_shap':np.abs(values).mean(axis=0)}).sort_values('mean_abs_shap',ascending=False); importance.to_csv(a.reports_dir/f'{a.target}_xgboost_shap_global_v01.csv',index=False)
 top=importance.head(15).sort_values('mean_abs_shap'); fig,ax=plt.subplots(figsize=(8,5)); ax.barh(top.feature,top.mean_abs_shap,color='#1f77b4'); ax.set(xlabel='Mean absolute SHAP value',title=f'Global SHAP importance: {a.target}'); fig.tight_layout(); fig.savefig(a.figures_dir/f'{a.target}_xgboost_shap_global_v01.png',dpi=180); plt.close(fig)
if __name__=='__main__': main()
