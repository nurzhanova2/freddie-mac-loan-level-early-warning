# Chapter 5. Explainability, stability and model-risk governance

## 5.1. Role of explanation

For the leading nonlinear model, TreeSHAP is used at both global and local
levels. Global importance shows the variables on which the model relies across
the evaluated sample, while local explanations decompose an individual alert
score into feature contributions. These quantities describe the fitted model,
rather than causal effects of borrower or loan characteristics [54], [55].

For formal adverse status, the most influential variables include original
interest rate, current delinquency status, FICO, loan age, DTI, and LTV/CLTV.
Their prominence is an empirical property of this model and sample; it does not
show that changing any one variable would change the outcome. The global audit
is reported in **Figure 5.1** — [“Global SHAP: formal adverse”](../../../reports/figures/models/formal_adverse_6m_xgboost_shap_global_v01.png)
and **Table 5.1** — [“Global SHAP importance”](../../../reports/models/formal_adverse_6m_xgboost_shap_global_v01.csv).

## 5.2. Stability assessment

An explanation is more useful for model governance when its principal rankings
are not driven by a single period. The temporal rank correlations are 0.994615
for formal adverse status and 0.984609 for early deterioration. These values
indicate strong agreement in the ranked contributions within the periods tested,
but they do not establish stability outside the selected cohorts or future
market conditions. Local explanations were also generated for Red and Amber
alerts to support case-level review. Stability assessment is material because
class imbalance and changes in observation composition can affect both scoring
quality and interpretations [11].

## 5.3. Governance implications

Reproducibility is supported through a data manifest, variable dictionary,
outcome and censoring specification, leakage register, temporal split,
calibration records, and trigger-policy configuration. This documentation
allows a prediction to be connected to the data and model version from which it
was produced. If a predictor is found to contain information unavailable at the
prediction date, the associated model evaluation and explanations must be
treated as invalid until the model is rebuilt with an admissible feature set.
This documentation framework is consistent with transparency, auditability, and
model-control requirements in credit-risk settings [5], [7], [55], [56].

An alert is a prioritisation instrument, not a decision rule. The Red tier is
used for the formal-adverse top-1% review capacity, while Amber signals support
watchlist monitoring. The threshold policy is specified in
[the versioned configuration](../../../config/fannie_suptech_trigger_policy_v01.yml).

## 5.4. Interpretation boundary

The completed SHAP audit provides evidence about the transparency and internal
stability of the fitted model. Independent Q1/Q3 comparison gives rank
correlations of 0.9962 for formal adverse status and 0.9938 for early
deterioration, with top-ten overlap of 10 and 9. It neither substitutes for
external validation nor determines the substantive reason for a particular
borrower's deterioration. The global-factor comparison is shown in **Figure
5.2** — [“Q1/Q3 SHAP factors”](../../../reports/figures/q3_shap_v01/formal_adverse_6m_q1_q3_shap_comparison_v01.png).
Detailed results are available in the [stage-15](../15_explainability_execution_report.md) and
[stage-23](../23_q3_explainability_governance_execution_report.md) reports.
