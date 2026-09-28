# Chapter 5. Explainability, stability and model-risk governance

## 5.1. Role of explanation

TreeSHAP is applied to the leading nonlinear model at global and local levels.
Global importance shows the variables on which the model relies in the
evaluated sample; local explanations decompose an individual alert score into
feature contributions. These quantities describe the fitted model rather than
causal effects of borrower or loan characteristics [25], [2].

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
can affect both scoring performance and interpretation [36].

### 5.2.1. Cross-method explanation check and cohort stability

TreeSHAP is supplemented with permutation importance and ALE on the unchanged
2017–2020 validation period. Permutation importance measures the loss of
ROC-AUC and PR-AUC after shuffling one raw feature, whereas SHAP characterises
feature contributions to individual scores. The methods are therefore not
interchangeable, particularly when predictors are correlated. For formal
adverse, the largest PR-AUC losses result from permuting current delinquency
status (0.263448), origination FICO (0.009453), and DTI (0.006797). For early
deterioration, the corresponding leading variables are FICO (0.039401),
modification flag (0.014363), and remaining months to maturity (0.012023).

SHAP and permutation rank agreement is 0.1662 for formal adverse and 0.7482
for early deterioration. The low value in the first case is not evidence that
either method is erroneous: they assess different properties of the frozen
model. It shows why a global explanation should not be reduced to a single
factor list. Results are reported in **Table 5.2** — [“Validation permutation
importance”](../../../reports/xai_extension_v01/formal_adverse_6m_validation_permutation_importance_v01.csv);
early-deterioration results appear in **Table 5.3** — [“Early-deterioration
permutation importance”](../../../reports/xai_extension_v01/early_deterioration_6m_validation_permutation_importance_v01.csv).
ALE profiles for leading numeric factors are shown in **Figures
5.3–5.4** — [formal adverse](../../../reports/figures/xai_extension_v01/formal_adverse_6m_validation_ale_v01.png)
and [early deterioration](../../../reports/figures/xai_extension_v01/early_deterioration_6m_validation_ale_v01.png).
They describe the functional form reproduced by the model in validation data
and have no causal interpretation.

Local explanation stability was also checked for alert queues from stress
(`2008Q1`, `2020Q1`) and reference (`2012Q1`, `2016Q1`) issuance cohorts. The
comparison is descriptive, not an estimate of a crisis or pandemic effect,
because cohorts differ in observation duration, composition, and survivor
selection. At the fixed top-1% Red capacity, mean-absolute-SHAP rank
correlation is 0.9762 and top-ten overlap is 10. At the top-5% Amber capacity,
the equivalent values are 0.9469 and 9. The comparison appears in **Figures
5.5–5.6** — [Red](../../../reports/figures/xai_extension_v01/formal_adverse_6m_alert_cohort_shap_comparison_v01.png)
and [Amber](../../../reports/figures/xai_extension_v01/early_deterioration_6m_alert_cohort_shap_comparison_v01.png).
Strong agreement in these groups supports internal explanation stability but
does not replace an external Freddie Mac validation.

## 5.3. Governance implications

Reproducibility is supported by a data manifest, variable dictionary, outcome
and censoring specification, leakage register, temporal split, calibration
records, and trigger-policy configuration. Together these artefacts link a
prediction to the data and model version from which it was obtained. If a
feature contains information unavailable at the prediction date, the model
evaluation and its explanations are invalid until the model is rebuilt with an
admissible feature set. This documentation framework is consistent with credit-
risk requirements for transparency, auditability, and model control [27], [28],
[2], [46].

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
and [stage-23](../23_q3_explainability_governance_execution_report.md) reports,
and in the [extended explainability audit](../27_extended_explainability_execution_report.md).
