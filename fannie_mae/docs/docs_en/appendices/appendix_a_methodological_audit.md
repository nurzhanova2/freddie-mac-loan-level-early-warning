# Appendix A. Methodological audit of data and models

## A.1. Purpose

This appendix records data provenance, transformation rules, outcome
definitions, temporal evaluation boundaries, and model specifications. It is
intended to make the empirical work reproducible and to distinguish documented
procedures from interpretive conclusions.

## A.2. Data source, structure, and glossary

The source is the Fannie Mae Single-Family Loan Performance Primary Dataset.
The official [file layout and glossary](../../sources/crt-file-layout-and-glossary.xlsx)
define field names, types, and economic meanings. Raw deliveries contain 113
positions; the analytical panel retains 35 fields needed for outcome derivation
and admissible predictors. The analytical unit is a loan-month observation.

The Q1 development workstream contains 185,931,842 loan-month observations and
3,343,420 loans. The extended Q1+Q3 workstream contains 467,638,404
observations and 8,272,539 loans counted across separate cohort panels; this is
not a globally deduplicated count of loan identifiers across raw archives.

## A.3. Cleaning, preparation, and leakage control

1. Archives are checked for field count, non-empty loan-identifier/reporting-
   month keys, and repeated keys.
2. Blank and whitespace-only values become missing values; `MMYYYY` fields are
   converted to calendar dates; analytical numeric fields are cast to numeric
   types.
3. The cleaned 113-field layer is kept separately from the 35-field analytical
   panel.
4. Variables that can reveal a future outcome, including Zero Balance Code,
   Zero Balance Effective Date, and foreclosure/disposition fields, are
   excluded from predictors. The decisions are recorded in the [leakage register](../../../data/dictionaries/fannie_2008q1_leakage_register_v01.csv).
5. Q3 provenance and structural checks are recorded in the [Q3 audit](../17_q3_archive_audit_execution_report.md).

## A.4. Outcomes, horizon, and censoring

| Outcome | Future-window event | Horizon | Risk set | Censoring |
|---|---|---:|---|---|
| `formal_adverse_6m` | status 03–98, i.e., 90+ days past due | 6 months | all admissible observations | incomplete future window or unobserved future status |
| `early_deterioration_6m` | transition from current to 01–98, i.e., 30+ days past due | 6 months | loans current at *t* only | same rule |

Codes XX and 99 are not events. Prepayment, maturity, and zero-balance
termination are not labelled as default. The complete procedure is in the
[Stages 7–9 report](../07_09_execution_report.md).

The sensitivity analysis additionally constructs three-, six-, and twelve-
month versions of both outcomes under the same risk-set and censoring rules.
For a fair comparison, their common OOT interval ends in March 2025, the last
month with a complete twelve-month future window. These versions do not replace
the principal six-month outcomes or the Red/Amber policy; results are recorded
in [the horizon-comparison report](../26_horizon_sensitivity_execution_report.md).

## A.5. Temporal split and actual training samples

The v01 baseline uses January 2006–December 2016 for training, January
2017–December 2020 for validation, and January 2021–September 2025 for the
independent out-of-time test. The last date preserves a complete six-month
outcome window because the delivery ends in March 2026.

The v01 models were not trained with the full record population loaded into
memory. A deterministic hash rule formed a case-control training sample and
1% temporal validation/out-of-time samples at natural event rates:

| Outcome | Train, observations (events) | Validation, observations (events) | OOT, observations (events) |
|---|---:|---:|---:|
| `formal_adverse_6m` | 628,102 (228,320) | 337,541 (3,732) | 658,314 (3,192) |
| `early_deterioration_6m` | 604,627 (205,659) | 332,693 (10,040) | 651,914 (15,242) |

In the extended v02 Q1+Q3 comparison, training samples contain 1,262,399
observations (420,588 events) for `formal_adverse_6m` and 1,240,046
observations (396,152 events) for `early_deterioration_6m`. This is a separate
extension experiment; it does not replace the v01 baseline results.

Relative to the full Q1+Q3 panel of 467,638,404 observations, these volumes
equal approximately 0.270% and 0.265%, respectively. These percentages do not
denote simple random samples: the full panel is used as a common denominator,
while train is restricted to the earlier temporal period and the case-control
rule intentionally enriches rare outcome observations. Accordingly, the thesis
reports the percentage together with the sampling design and does not interpret
it as the share of randomly selected rows.

Training-size sensitivity analysis has been completed for XGBoost as the
leading candidate for each outcome. Nested 1%, 5%, 10%, and 25% natural-rate
samples were formed in the Q1 training period; validation remained unchanged,
and OOT was used once to assess the already frozen models. Results and
limitations are reported in the [Stages 5–7 report](../25_train_size_sensitivity_oot_execution_report.md).

## A.6. Model parameters, calibration, and trigger policy

| Component | Fixed v01 specification |
|---|---|
| Logistic regression | `solver=saga`, `max_iter=120`, `C=1.0`, `random_state=42` |
| XGBoost | 160 trees, depth 6, `learning_rate=0.08`, `min_child_weight=10`, `subsample=0.8`, `colsample_bytree=0.8`, `tree_method=hist`, `random_state=42` |
| CatBoost (extended v02 comparison) | 180 iterations, depth 6, `learning_rate=0.08`, `Logloss`, `random_seed=42` |
| LightGBM (extended v02 comparison) | 180 trees, depth 6, `learning_rate=0.08`, `min_child_samples=20`, `subsample=0.8`, `colsample_bytree=0.8`, `random_state=42` |
| Calibration | isotonic regression fitted only on validation; OOT is not used to fit the calibrator |
| Red alert | `formal_adverse_6m`, top-1% review capacity; OOT precision 24.29%, recall 50.09% |
| Amber alert | `early_deterioration_6m`, top-5% review capacity; OOT precision 8.69%, recall 18.59% |

The [versioned policy](../../../config/fannie_suptech_trigger_policy_v01.yml)
explicitly prohibits autonomous supervisory or enforcement action. An alert
only prioritises human review and is accompanied by a local explanation.

Model parameters were defined *a priori* as regularised, computationally
feasible baseline specifications. Grid/random search, Bayesian optimisation,
and Optuna were not used, and the parameters are not claimed to be optimal for
Fannie Mae. The decision makes comparison uniform but leaves validation-only
hyperparameter tuning as subsequent work.

## A.7. Control artefacts

- [Temporal-split summary](../../../reports/splits/fannie_temporal_split_v01_summary.csv)
- [Baseline metrics summary](../../../reports/models/final_dissertation_summary_v01.csv)
- [Model comparison](../../../reports/models/final_model_comparison_v01.csv)
- [Q1/Q3 comparison](../../../reports/q1_q3_robustness_v01/02_matched_q1_q3_comparison.csv)
- [Q1/Q3 SHAP stability: formal adverse](../../../reports/q3_shap_v01/formal_adverse_6m_q1_q3_shap_stability_v01.csv)
- [Q1/Q3 SHAP stability: early deterioration](../../../reports/q3_shap_v01/early_deterioration_6m_q1_q3_shap_stability_v01.csv)
- [Permutation importance: formal adverse](../../../reports/xai_extension_v01/formal_adverse_6m_validation_permutation_importance_v01.csv)
- [Permutation importance: early deterioration](../../../reports/xai_extension_v01/early_deterioration_6m_validation_permutation_importance_v01.csv)
- [Red/Amber cohort-group SHAP stability audit](../../../reports/xai_extension_v01/xai_alert_cohort_shap_audit_summary_v01.csv)
