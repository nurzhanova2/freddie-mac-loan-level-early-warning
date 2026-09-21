#!/usr/bin/env python3
"""Create a compact final-results figure and summary table for Chapter 6."""
from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd

reports=Path('fannie_mae/reports/models'); figures=Path('fannie_mae/reports/figures/final_v01'); figures.mkdir(parents=True,exist_ok=True)
models=pd.read_csv(reports/'final_model_comparison_v01.csv')
formal=pd.read_csv(reports/'formal_adverse_6m_xgboost_alert_policy_v01.csv')
early=pd.read_csv(reports/'early_deterioration_6m_xgboost_alert_policy_v01.csv')
summary=pd.DataFrame([
 {'component':'Formal adverse XGBoost','metric':'ROC-AUC','value':0.894333},
 {'component':'Formal adverse XGBoost','metric':'PR-AUC','value':0.286618},
 {'component':'Early deterioration XGBoost','metric':'ROC-AUC','value':0.730995},
 {'component':'Early deterioration XGBoost','metric':'PR-AUC','value':0.066271},
 {'component':'Formal adverse top 1% trigger','metric':'Recall, %','value':50.093985},
 {'component':'Formal adverse top 1% trigger','metric':'Precision, %','value':24.289837},
 {'component':'Early deterioration top 5% trigger','metric':'Recall, %','value':18.5868},
 {'component':'Early deterioration top 5% trigger','metric':'Precision, %','value':8.69125},
])
summary.to_csv(reports/'final_dissertation_summary_v01.csv',index=False)
plt.style.use('seaborn-v0_8-whitegrid'); fig,(a,b)=plt.subplots(1,2,figsize=(12,4.8))
for target,label in [('formal_adverse_6m','Formal adverse'),('early_deterioration_6m','Early deterioration')]:
 x=models[models.target==target]; a.bar([label+'\nROC-AUC',label+'\nPR-AUC'],[x[x.model=='xgboost'].roc_auc.iloc[0],x[x.model=='xgboost'].pr_auc.iloc[0]],color=['#1f77b4','#4c9bd2'])
a.set_ylim(0,1);a.set_title('XGBoost: out-of-time discrimination');a.set_ylabel('Score')
policy=pd.concat([formal.assign(policy='Formal adverse\ntop 1%').query('alert_capacity_pct == 1'),early.assign(policy='Early deterioration\ntop 5%').query('alert_capacity_pct == 5')])
x=range(len(policy));b.bar([i-.18 for i in x],policy.precision_pct,.36,label='Precision');b.bar([i+.18 for i in x],policy.recall_pct,.36,label='Recall');b.set_xticks(list(x),policy.policy);b.set_ylim(0,100);b.set_ylabel('%');b.set_title('Selected alert policies');b.legend()
fig.tight_layout();fig.savefig(figures/'final_model_and_trigger_summary_v01.png',dpi=180);plt.close(fig)
