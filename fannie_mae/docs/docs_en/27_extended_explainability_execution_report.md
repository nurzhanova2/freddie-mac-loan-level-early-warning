# Stage 24. Extended explainability audit of the leading models

## Purpose and scope

The audit uses the frozen XGBoost models for `formal_adverse_6m` and
`early_deterioration_6m`. It supplements the existing global and local
TreeSHAP artefacts. No model was refitted, and neither hyperparameters nor
queue capacities were changed. Permutation importance and ALE were calculated
only on the January 2017–December 2020 validation period; the OOT period was
not used for a further model, threshold, or explanation choice.

Permutation importance measures the change in ROC-AUC and PR-AUC after one raw
feature is randomly shuffled while the other features remain unchanged. It
describes that feature's contribution to ranking quality in this fitted model.
With correlated features it is not a causal effect and need not match mean
absolute SHAP ranks. ALE profiles show the local change in the uncalibrated
score when a numeric feature varies within empirical intervals. They are not
used to infer a feature's effect on risk.

## SHAP and permutation-importance comparison

For `formal_adverse_6m`, using a deterministic 30,000-observation validation
sample, the largest PR-AUC losses arise from permuting current delinquency
status (0.263448), origination FICO (0.009453), DTI (0.006797), and number of
borrowers (0.004637). For `early_deterioration_6m`, the leading losses arise
from origination FICO (0.039401), modification flag (0.014363), remaining
months to maturity (0.012023), and original interest rate (0.008470).

The rank correlation between permutation and SHAP importance is 0.1662 for
formal adverse and 0.7482 for early deterioration. The methods address
different quantities: SHAP allocates contributions to individual scores,
whereas permutation importance measures the loss of ranking performance after
breaking a feature's relation to the outcome. Low agreement in the former case
is therefore not evidence of contradictory explanations. It limits replacing
one method with the other and supports their joint use.

ALE profiles were produced for the four most relevant numeric variables of each
outcome: FICO, DTI, number of borrowers, and remaining maturity for formal
adverse; FICO, remaining maturity, original interest rate, and remaining legal
maturity for early deterioration. The profiles describe the functional form
reproduced by the model in validation data and carry no causal interpretation.

## Alert explanations across issuance cohorts

For a descriptive explanation check, validation alerts were divided into two
issuance groups. The stress group comprises `2008Q1` and `2020Q1`; the
reference group comprises `2012Q1` and `2016Q1`. This comparison describes
explanations among loans observed in validation. It is not an estimate of a
financial-crisis or pandemic effect: groups differ in observation duration,
loan composition, and survivor selection.

For formal adverse, the fixed top-1% Red capacity was applied within each group:
719 stress alerts and 1,000 reference alerts entered the SHAP audit. The rank
correlation of mean absolute SHAP is 0.9762 and the top-ten overlap is 10. For
early deterioration, the fixed top-5% Amber capacity supplied 1,000 alerts per
group; the corresponding values are 0.9469 and 9. Explanations show substantial
agreement inside these cohort groups, but this does not substitute for an
independent external validation.

## Artefacts

- [Permutation importance: formal adverse](../../reports/xai_extension_v01/formal_adverse_6m_validation_permutation_importance_v01.csv);
- [Permutation importance: early deterioration](../../reports/xai_extension_v01/early_deterioration_6m_validation_permutation_importance_v01.csv);
- [ALE: formal adverse](../../reports/figures/xai_extension_v01/formal_adverse_6m_validation_ale_v01.png);
- [ALE: early deterioration](../../reports/figures/xai_extension_v01/early_deterioration_6m_validation_ale_v01.png);
- [Red SHAP comparison: stress/reference](../../reports/figures/xai_extension_v01/formal_adverse_6m_alert_cohort_shap_comparison_v01.png);
- [Amber SHAP comparison: stress/reference](../../reports/figures/xai_extension_v01/early_deterioration_6m_alert_cohort_shap_comparison_v01.png);
- [reproducible script](../../../src/fannie_mae/audit_fannie_xai_extension.py).
