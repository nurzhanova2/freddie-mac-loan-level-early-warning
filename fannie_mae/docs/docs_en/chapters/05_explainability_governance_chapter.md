# Chapter 5. Explainability, stability and model-risk governance

## 5.1. Role of explanation

TreeSHAP is applied to the leading nonlinear model at global and local levels.
Global importance shows the variables on which the model relies in the
evaluated sample; local explanations decompose an individual alert score into
feature contributions. These quantities describe the fitted model rather than
causal effects of borrower or loan characteristics [54], [55].

For formal adverse status, the most influential variables are original interest
rate, current delinquency status, FICO, loan age, DTI, and LTV/CLTV. Their
prominence is an empirical property of the model and the sample, not evidence
that changing one variable would change the outcome. The global audit is shown
in **Figure 5.1** — [“Global SHAP: formal adverse”](../../../reports/figures/models/formal_adverse_6m_xgboost_shap_global_v01.png)
and **Table 5.1** — [“Global SHAP importance”](../../../reports/models/formal_adverse_6m_xgboost_shap_global_v01.csv).

## 5.2. Stability assessment

Model-risk governance requires that the ranking of principal factors is not
driven by a single period. Temporal rank correlations are 0.994615 for formal
adverse status and 0.984609 for early deterioration. They indicate strong
agreement within the periods tested, but do not establish stability outside the
selected cohorts or under future market conditions. Local explanations were
also generated for Red and Amber alerts to support case-level review. This
assessment matters because class imbalance and changes in the observation mix
can affect both scoring performance and interpretation [11].

## 5.3. Governance implications

Reproducibility is supported by a data manifest, variable dictionary, outcome
and censoring specification, leakage register, temporal split, calibration
records, and trigger-policy configuration. Together these artefacts link a
prediction to the data and model version from which it was obtained. If a
feature contains information unavailable at the prediction date, the model
evaluation and its explanations are invalid until the model is rebuilt with an
admissible feature set. This documentation framework is consistent with credit-
risk requirements for transparency, auditability, and model control [5], [7],
[55], [56].

An alert is a prioritisation instrument rather than a decision rule. Red is
assigned to the formal-adverse top-1% review capacity; Amber supports watchlist
monitoring. The threshold policy is specified in [the versioned configuration](../../../config/fannie_suptech_trigger_policy_v01.yml).

## 5.4. Interpretation boundary

The SHAP audit characterises the transparency and internal stability of the
fitted model. Independent Q1/Q3 comparison yields rank correlations of 0.9962
for formal adverse and 0.9938 for early deterioration, with top-ten feature
overlap of 10 and 9. This evidence neither substitutes for external validation
nor identifies the substantive cause of deterioration for an individual loan.
The global-factor comparison is shown in **Figure 5.2** — [“Q1/Q3 SHAP factors”](../../../reports/figures/q3_shap_v01/formal_adverse_6m_q1_q3_shap_comparison_v01.png).
Detailed results are available in the [stage-15](../15_explainability_execution_report.md)
and [stage-23](../23_q3_explainability_governance_execution_report.md) reports.
