#!/usr/bin/env python3
"""Compare global TreeSHAP rankings of frozen Q1 XGBoost on Q1 and Q3 samples."""
from __future__ import annotations
import argparse
from pathlib import Path
import joblib, matplotlib.pyplot as plt, numpy as np, pandas as pd, xgboost as xgb
from evaluate_fannie_alert_policy import FEATURES
def importance(model, frame):
 x=model.named_steps['preprocess'].transform(frame[FEATURES]); names=model.named_steps['preprocess'].get_feature_names_out(); z=model.named_steps['model'].get_booster().predict(xgb.DMatrix(x,feature_names=list(names)),pred_contribs=True)[:,:-1]
 return pd.Series(np.abs(z).mean(axis=0),index=names)
def main():
 p=argparse.ArgumentParser();p.add_argument('--target',choices=['formal_adverse_6m','early_deterioration_6m'],required=True);p.add_argument('--n',type=int,default=5000);p.add_argument('--q1-samples',type=Path,default=Path('fannie_mae/data/model_samples_v01'));p.add_argument('--q3-samples',type=Path,default=Path('fannie_mae/data/q3_control_samples_v01'));p.add_argument('--models',type=Path,default=Path('fannie_mae/models/xgboost_v01'));p.add_argument('--out',type=Path,default=Path('fannie_mae/reports/q3_shap_v01'));p.add_argument('--figures',type=Path,default=Path('fannie_mae/reports/figures/q3_shap_v01'));a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True);a.figures.mkdir(parents=True,exist_ok=True)
 m=joblib.load(a.models/f'{a.target}_xgboost_v01.joblib');q1=pd.read_parquet(a.q1_samples/f'{a.target}_out_of_time_test_sample_v01.parquet').sample(n=a.n,random_state=42);q3=pd.read_parquet(a.q3_samples/f'{a.target}_q3_control_sample_v01.parquet').sample(n=a.n,random_state=42)
 one,two=importance(m,q1),importance(m,q3);d=pd.DataFrame({'feature':one.index,'q1_mean_abs_shap':one.values,'q3_mean_abs_shap':two.reindex(one.index).values});d['q1_rank']=d.q1_mean_abs_shap.rank(ascending=False,method='min');d['q3_rank']=d.q3_mean_abs_shap.rank(ascending=False,method='min');d['rank_change']=(d.q1_rank-d.q3_rank).abs();d.sort_values('q3_mean_abs_shap',ascending=False).to_csv(a.out/f'{a.target}_q1_q3_shap_comparison_v01.csv',index=False)
 top=d.nsmallest(12,'q3_rank').sort_values('q3_mean_abs_shap');fig,ax=plt.subplots(figsize=(9,5));ax.barh(top.feature,top.q1_mean_abs_shap,label='Q1',alpha=.75);ax.barh(top.feature,top.q3_mean_abs_shap,label='Q3',alpha=.75);ax.legend();ax.set(xlabel='Mean absolute SHAP',title=f'Q1/Q3 SHAP comparison: {a.target}');fig.tight_layout();fig.savefig(a.figures/f'{a.target}_q1_q3_shap_comparison_v01.png',dpi=180);plt.close(fig)
 pd.DataFrame([{'target':a.target,'q1_q3_spearman_rank_correlation':d.q1_rank.corr(d.q3_rank,method='spearman'),'top_10_overlap':len(set(d.nsmallest(10,'q1_rank').feature)&set(d.nsmallest(10,'q3_rank').feature))}]).to_csv(a.out/f'{a.target}_q1_q3_shap_stability_v01.csv',index=False)
if __name__=='__main__':main()
