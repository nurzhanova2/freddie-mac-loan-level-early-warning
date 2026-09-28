# List of tables and figures

This register is the single numbering reference for the dissertation's main
version. Numbers, captions, and in-text references must match these entries.
Links point to reproducible project artefacts.

## Tables

| Number | Caption | Artefact |
|---|---|---|
| Table 2.1 | Coverage of Fannie Mae Q1 cohorts | [CSV](../../../reports/eda_v01/01_cohort_overview.csv) |
| Table 2.2 | Loan origination characteristics by cohort | [CSV](../../../reports/eda_v01/03_origination_characteristics.csv) |
| Table 3.1 | Six-month outcomes by Q1 cohort | [CSV](../../../reports/eda_v01/05_six_month_outcome_summary.csv) |
| Table 3.2 | Distribution of current delinquency status | [CSV](../../../reports/eda_v01/04_current_delinquency_distribution.csv) |
| Table 3.3 | Comparison of matched Q1 and Q3 cohorts | [CSV](../../../reports/q1_q3_robustness_v01/02_matched_q1_q3_comparison.csv) |
| Table 4.1 | Temporal train, validation, and out-of-time split | [CSV](../../../reports/splits/fannie_temporal_split_v01_summary.csv) |
| Table 4.2 | Logistic benchmark metrics | [CSV](../../../reports/models/logistic_baseline_v01_summary.csv) |
| Table 4.3 | Probability-calibration comparison | [CSV](../../../reports/models/logistic_isotonic_calibration_v01_summary.csv) |
| Table 4.4 | OOT-metric sensitivity to natural-rate training size | [CSV](../../../reports/train_size_sensitivity_v01/train_size_oot_metrics_summary_v01.csv) |
| Table 4.5 | Common-OOT comparison of 3-, 6-, and 12-month horizons | [CSV](../../../reports/horizon_sensitivity_v01/horizon_oot_comparability_summary_v01.csv) |
| Table 5.1 | Global SHAP importance for formal adverse | [CSV](../../../reports/models/formal_adverse_6m_xgboost_shap_global_v01.csv) |
| Table 5.2 | Formal-adverse validation permutation importance | [CSV](../../../reports/xai_extension_v01/formal_adverse_6m_validation_permutation_importance_v01.csv) |
| Table 5.3 | Early-deterioration validation permutation importance | [CSV](../../../reports/xai_extension_v01/early_deterioration_6m_validation_permutation_importance_v01.csv) |
| Table 5.4 | Red and Amber SHAP stability across cohort groups | [CSV](../../../reports/xai_extension_v01/xai_alert_cohort_shap_audit_summary_v01.csv) |
| Table 6.1 | Logistic Regression and XGBoost comparison | [CSV](../../../reports/models/final_model_comparison_v01.csv) |
| Table 6.2 | Final model and trigger-policy metrics | [CSV](../../../reports/models/final_dissertation_summary_v01.csv) |
| Table A.1 | Model parameters, calibration, and alert thresholds | [Appendix A](appendix_a_methodological_audit.md) |
| Table B.1 | Data lineage from source archive to safe alert export | [Appendix B](appendix_b_data_lineage_and_glossary.md) |
| Table B.2 | Working glossary of data, outcomes, and alerts | [Appendix B](appendix_b_data_lineage_and_glossary.md) |

## Figures

| Number | Caption | Artefact |
|---|---|---|
| Figure 2.1 | Origination characteristics across Q1 cohorts | [PNG](../../../reports/figures/eda_v01/03_origination_characteristics_trend.png) |
| Figure 3.1 | Six-month outcome rates across Q1 cohorts | [PNG](../../../reports/figures/eda_v01/01_six_month_outcome_rates_by_cohort.png) |
| Figure 3.2 | Distribution of current delinquency status | [PNG](../../../reports/figures/eda_v01/02_current_delinquency_distribution.png) |
| Figure 3.3 | Calendar trend in current delinquency | [PNG](../../../reports/figures/eda_v01/05_calendar_month_delinquency_trend.png) |
| Figure 3.4 | Q1/Q3 six-month outcome comparison | [PNG](../../../reports/figures/q1_q3_robustness_v01/01_q1_q3_outcome_comparison.png) |
| Figure 4.1 | Chronological sample split | [PNG](../../../reports/figures/splits/fannie_temporal_split_timeline_v01.png) |
| Figure 4.2 | Formal-adverse probability calibration | [PNG](../../../reports/figures/models/formal_adverse_6m_calibration_v01.png) |
| Figure 4.3 | Early-deterioration probability calibration | [PNG](../../../reports/figures/models/early_deterioration_6m_calibration_v01.png) |
| Figure 4.4 | Formal-adverse OOT metrics by training size | [PNG](../../../reports/figures/train_size_sensitivity_v01/formal_adverse_6m_train_size_oot_metrics_v01.png) |
| Figure 4.5 | Early-deterioration OOT metrics by training size | [PNG](../../../reports/figures/train_size_sensitivity_v01/early_deterioration_6m_train_size_oot_metrics_v01.png) |
| Figure 4.6 | Formal-adverse OOT reliability across training sizes | [PNG](../../../reports/figures/train_size_sensitivity_v01/formal_adverse_6m_train_size_oot_calibration_v01.png) |
| Figure 4.7 | Early-deterioration OOT reliability across training sizes | [PNG](../../../reports/figures/train_size_sensitivity_v01/early_deterioration_6m_train_size_oot_calibration_v01.png) |
| Figure 4.8 | Prevalence-adjusted formal-adverse OOT horizon comparison | [PNG](../../../reports/figures/horizon_sensitivity_v01/formal_adverse_horizon_oot_comparability_v01.png) |
| Figure 4.9 | Prevalence-adjusted early-deterioration OOT horizon comparison | [PNG](../../../reports/figures/horizon_sensitivity_v01/early_deterioration_horizon_oot_comparability_v01.png) |
| Figure 5.1 | Global SHAP importance for formal adverse | [PNG](../../../reports/figures/models/formal_adverse_6m_xgboost_shap_global_v01.png) |
| Figure 5.2 | Q1/Q3 SHAP-factor comparison for formal adverse | [PNG](../../../reports/figures/q3_shap_v01/formal_adverse_6m_q1_q3_shap_comparison_v01.png) |
| Figure 5.3 | Formal-adverse validation ALE profiles | [PNG](../../../reports/figures/xai_extension_v01/formal_adverse_6m_validation_ale_v01.png) |
| Figure 5.4 | Early-deterioration validation ALE profiles | [PNG](../../../reports/figures/xai_extension_v01/early_deterioration_6m_validation_ale_v01.png) |
| Figure 5.5 | Red-alert SHAP comparison: stress and reference cohorts | [PNG](../../../reports/figures/xai_extension_v01/formal_adverse_6m_alert_cohort_shap_comparison_v01.png) |
| Figure 5.6 | Amber-alert SHAP comparison: stress and reference cohorts | [PNG](../../../reports/figures/xai_extension_v01/early_deterioration_6m_alert_cohort_shap_comparison_v01.png) |
| Figure 6.1 | Final model and trigger-policy comparison | [PNG](../../../reports/figures/final_v01/final_model_and_trigger_summary_v01.png) |

## In-text reference rule

Use “see Figure 3.4” or “results are reported in Table 6.1.” Figure captions
appear below figures and table captions above tables. Captions state the
substantive title rather than the file name; the source should be given as
“author’s calculations using Fannie Mae data,” with the artefact version noted
in an appendix or footnote.

Methodological definitions and data lineage are provided in [Appendices A–B](appendix_a_methodological_audit.md).
