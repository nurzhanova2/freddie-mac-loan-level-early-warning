#!/usr/bin/env python3
"""Assess global SHAP importance stability across validation, OOT, and cohorts."""
from __future__ import annotations
import argparse,json
from pathlib import Path
import joblib,numpy as np,pandas as pd,xgboost as xgb
from evaluate_fannie_alert_policy import FEATURES

def importance(model,frame):
 X=model.named_steps['preprocess'].transform(frame[FEATURES]); names=model.named_steps['preprocess'].get_feature_names_out()
 values=model.named_steps['model'].get_booster().predict(xgb.DMatrix(X,feature_names=list(names)),pred_contribs=True)[:,:-1]
 return pd.Series(np.abs(values).mean(axis=0),index=names)
def main():
 p=argparse.ArgumentParser(); p.add_argument('--target',choices=['formal_adverse_6m','early_deterioration_6m'],required=True); p.add_argument('--sample-size',type=int,default=5000); p.add_argument('--samples-dir',type=Path,default=Path('fannie_mae/data/model_samples_v01')); p.add_argument('--models-dir',type=Path,default=Path('fannie_mae/models/xgboost_v01')); p.add_argument('--reports-dir',type=Path,default=Path('fannie_mae/reports/models')); a=p.parse_args(); a.reports_dir.mkdir(parents=True,exist_ok=True)
 model=joblib.load(a.models_dir/f'{a.target}_xgboost_v01.joblib'); val=pd.read_parquet(a.samples_dir/f'{a.target}_validation_sample_v01.parquet').sample(n=a.sample_size,random_state=42); oot=pd.read_parquet(a.samples_dir/f'{a.target}_out_of_time_test_sample_v01.parquet').sample(n=a.sample_size,random_state=42)
 v=importance(model,val); o=importance(model,oot); result=pd.DataFrame({'feature':v.index,'validation_mean_abs_shap':v.values,'oot_mean_abs_shap':o.reindex(v.index).values}); result['validation_rank']=result.validation_mean_abs_shap.rank(ascending=False,method='min').astype(int); result['oot_rank']=result.oot_mean_abs_shap.rank(ascending=False,method='min').astype(int); result['absolute_rank_change']=(result.validation_rank-result.oot_rank).abs(); result.sort_values('oot_mean_abs_shap',ascending=False).to_csv(a.reports_dir/f'{a.target}_xgboost_shap_temporal_stability_v01.csv',index=False)
 cohort_rows=[]
 for cohort,group in oot.groupby('acquisition_cohort'):
  if len(group)>=100: 
   z=importance(model,group)
   for feature,value in z.items(): cohort_rows.append({'acquisition_cohort':cohort,'feature':feature,'mean_abs_shap':value})
 pd.DataFrame(cohort_rows).to_csv(a.reports_dir/f'{a.target}_xgboost_shap_cohort_stability_v01.csv',index=False)
 payload={'target':a.target,'sample_size_per_period':a.sample_size,'spearman_rank_correlation':round(float(result.validation_rank.corr(result.oot_rank,method='spearman')),6),'top_10_overlap':int(len(set(result.nsmallest(10,'validation_rank').feature)&set(result.nsmallest(10,'oot_rank').feature)))}
 (a.reports_dir/f'{a.target}_xgboost_shap_stability_v01.json').write_text(json.dumps(payload,indent=2)+'\n')
if __name__=='__main__': main()
