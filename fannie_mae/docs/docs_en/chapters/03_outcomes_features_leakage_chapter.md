# Chapter 3. Outcomes, features and information-leakage control

## 3.1. Temporal logic of prediction

Each loan-month defines a prediction date. Predictors use only information
available at or before month *t*, whereas the outcome is realised in the
following three- or six-month window. This ordering distinguishes early warning
from retrospective classification and is consistent with dynamic and survival
approaches to credit risk [40], [38], [39].

## 3.2. Outcome definitions and censoring

Formal adverse status is defined by a future delinquency status from 03 to 98,
corresponding to 90+ days past due. Early deterioration is defined only for
loans current at *t* and records a subsequent status from 01 to 98, or 30+ days
past due. Codes XX and 99 are not events. Prepayment, maturity, and zero-balance
termination are not recoded as default. When the future window is incomplete or
the future status is unobserved, the observation is censored rather than
labelled as a non-event. Status and code treatment follows the official Fannie
Mae specification [48].

## 3.3. Predictor admissibility

Candidate predictors include origination characteristics, contemporaneous
balance, rate and loan-age measures, and payment states available before the
prediction date. The [leakage register](../../../data/dictionaries/fannie_2008q1_leakage_register_v01.csv)
documents treatment of all 113 source fields. Zero Balance Code, Zero Balance
Effective Date, foreclosure/disposition fields, and other post-event variables
are excluded because they may reveal information produced after the prediction
date. The exclusion is therefore auditable and consistent with requirements for
temporally admissible credit-modelling data [2], [46].

## 3.4. Label construction and descriptive evidence

In the initial 2008Q1 panel, six-month formal adverse status is observed in
503,395 of 18,986,874 labelled observations; early deterioration is observed
in 1,277,828 of 18,168,886. The corresponding three-month figures are 264,892
of 20,007,896 and 758,624 of 19,152,309. Versioned definitions and quality
checks are documented in the [Stages 7–9 report](../07_09_execution_report.md).

Across seven cohorts, six-month early-deterioration and formal-adverse rates are
highest for 2008Q1 (7.033% and 2.651%) and lower for 2012Q1 (1.353% and
0.231%). These differences show heterogeneity within the study sample and
support retaining acquisition-cohort information and using temporal validation.
They are not estimates of mortgage risk for the United States as a whole. The
evidence is shown in **Figure 3.1** — [“Six-month outcomes by cohort”](../../../reports/figures/eda_v01/01_six_month_outcome_rates_by_cohort.png)
and **Table 3.1** — [“Six-month outcome summary”](../../../reports/eda_v01/05_six_month_outcome_summary.csv).

## 3.5. Interpretation boundary

The two outcomes operationalise subsequent deterioration in payment behaviour;
they do not provide a universal definition of default. Their interpretation
depends on the stated data-generating setting and forecast horizon. The
distribution of current delinquency statuses and their calendar trend appear in
**Figures 3.2–3.3** — [“Distribution of current delinquency status”](../../../reports/figures/eda_v01/02_current_delinquency_distribution.png)
and [“Calendar trend in delinquency”](../../../reports/figures/eda_v01/05_calendar_month_delinquency_trend.png) —
and in the [stage-11 report](../11_exploratory_data_analysis_report.md).

## 3.6. Comparison of Q1 and Q3 cohorts

Q1 and Q3 cohorts from matched acquisition years differ in origination
characteristics and subsequent outcome rates. In 2020, the six-month
formal-adverse rate is 1.0113% for Q1 and 0.2646% for Q3; the early-
deterioration rate is 2.6480% and 1.5580%, respectively. In 2022, the direction
reverses: formal-adverse rates are 0.5304% for Q1 and 0.8374% for Q3, while
early-deterioration rates are 2.5353% and 3.2676%. Origination quarter therefore
cannot be treated as a neutral substitute within a calendar year. This result
motivates independent Q3 model evaluation but does not identify the cause of
the differences. Results are shown in **Figure 3.4** — [“Q1/Q3 outcome comparison”](../../../reports/figures/q1_q3_robustness_v01/01_q1_q3_outcome_comparison.png)
and **Table 3.3** — [“Matched Q1/Q3 comparison”](../../../reports/q1_q3_robustness_v01/02_matched_q1_q3_comparison.csv).
