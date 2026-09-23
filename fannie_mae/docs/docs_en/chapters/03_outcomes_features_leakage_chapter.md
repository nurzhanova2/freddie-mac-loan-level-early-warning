# Chapter 3. Outcomes, features and information-leakage control

## 3.1. Temporal logic of prediction

Each loan-month defines a prediction date. Predictors use only information
available at or before month *t*, whereas the outcome is realised in the
subsequent three- or six-month window. This ordering distinguishes early warning
from retrospective classification and is consistent with dynamic and survival
approaches to credit risk [6], [52], [53].

## 3.2. Outcome definitions and censoring

The formal-adverse outcome is a future delinquency status from 03 to 98,
corresponding to 90+ days past due. Early deterioration is defined only for
loans current at *t* and records a subsequent status from 01 to 98, corresponding
to 30+ days past due. Codes XX and 99 are not counted as events. Prepayment,
maturity, and zero-balance termination are not redefined as default. When a
future window is incomplete or the future status is not observed, the
observation is censored rather than labelled as a non-event. The treatment of
statuses and codes follows the official Fannie Mae delivery specification [57].

## 3.3. Predictor admissibility

The candidate predictor set comprises origination characteristics, contemporaneous
balance, rate and loan-age measures, and payment states available before the
prediction date. The [leakage register](../../../data/dictionaries/fannie_2008q1_leakage_register_v01.csv)
documents the treatment of all 113 source fields. Zero Balance Code, Zero
Balance Effective Date, foreclosure/disposition fields, and other post-event
variables are excluded because they can reveal information generated after the
prediction date. The register makes this methodological exclusion auditable.
This distinction is consistent with requirements for auditability and temporal
admissibility of data in credit modelling [55], [56].

## 3.4. Label construction and descriptive evidence

For the initial 2008Q1 panel, six-month formal adverse status is observed in
503,395 of 18,986,874 labelled observations; early deterioration is observed in
1,277,828 of 18,168,886 labelled observations. The corresponding three-month
figures are 264,892 of 20,007,896 and 758,624 of 19,152,309. Versioned
definitions and quality checks are documented in the [Stages 7–9 report](../07_09_execution_report.md).

Across seven cohorts, the six-month early-deterioration and formal-adverse rates
are highest for 2008Q1 (7.033% and 2.651%) and lower for 2012Q1 (1.353% and
0.231%). These differences demonstrate heterogeneity within the study sample
and justify retaining acquisition cohort information and using temporal
validation. They are not estimates of U.S.-wide mortgage risk. The evidence is
shown in **Figure 3.1** — [“Six-month outcomes by cohort”](../../../reports/figures/eda_v01/01_six_month_outcome_rates_by_cohort.png)
and **Table 3.1** — [“Six-month outcome summary”](../../../reports/eda_v01/05_six_month_outcome_summary.csv).

## 3.5. Interpretation boundary

The outcome definitions operationalise subsequent payment deterioration; they
do not constitute a universal definition of default. Their adequacy therefore
depends on the stated data-generating setting and forecast horizon. The
cohort-level delinquency distribution and calendar trend are reported in
**Figure 3.2** — [“Distribution of current delinquency status”](../../../reports/figures/eda_v01/02_current_delinquency_distribution.png),
**Figure 3.3** — [“Calendar trend in delinquency”](../../../reports/figures/eda_v01/05_calendar_month_delinquency_trend.png),
and the [stage-11 report](../11_exploratory_data_analysis_report.md).

## 3.6. Comparison of Q1 and Q3 cohorts

Matched acquisition years show that Q1 and Q3 cohorts differ in both
origination characteristics and subsequent outcome rates. In 2020, the
six-month formal-adverse rate is 1.0113% for Q1 and 0.2646% for Q3, while the
early-deterioration rate is 2.6480% and 1.5580%, respectively. In 2022, the
direction differs: formal-adverse rates are 0.5304% for Q1 and 0.8374% for Q3,
and early-deterioration rates are 2.5353% and 3.2676%. Thus, the origination
quarter cannot be treated as a neutral substitution within a calendar year.
This observation motivates independent Q3 model evaluation, but does not
identify the cause of the differences. Results are shown in **Figure 3.4** —
[“Q1/Q3 outcome comparison”](../../../reports/figures/q1_q3_robustness_v01/01_q1_q3_outcome_comparison.png)
and **Table 3.3** — [“Matched Q1/Q3 comparison”](../../../reports/q1_q3_robustness_v01/02_matched_q1_q3_comparison.csv).
