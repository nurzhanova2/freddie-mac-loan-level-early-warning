# Stage 11. Initial exploratory analysis and feature preparation

**Status: the initial exploratory analysis is complete; the baseline v01 safe
feature set is fixed.** The analysis is fully reproducible through `src/fannie_mae/analyze_fannie_eda.py`
and uses Fannie Mae processed panels only. Raw ZIP archives were not changed and
Freddie Mac data were not joined.

## 11.1. Coverage and unit of analysis

The analysis includes seven acquisition cohorts: 2006Q1, 2008Q1, 2012Q1,
2016Q1, 2020Q1, 2022Q1, and 2024Q1. Together, they contain **185,931,842**
loan-month observations and **3,343,420** loans. The loan count is summed by
cohort; cohorts are defined by origination quarter, so a loan should not belong
to two cohorts.

| Measure | Minimum / maximum across cohorts | Interpretation |
|---|---:|---|
| Number of loans | 188,502 / 793,818 | 2024Q1 has a shorter observed history |
| Mean origination FICO | 722.1 / 770.3 | descriptive, not a causal effect |
| Mean original LTV | 67.17% / 74.74% | computed at the loan's first observation |
| Mean original UPB | $181,966 / $325,561 | nominal loan amounts rise across vintages |

Detailed tables: [cohort coverage](../../reports/eda_v01/01_cohort_overview.csv)
and [origination characteristics](../../reports/eda_v01/03_origination_characteristics.csv).

## 11.2. Candidate-feature quality

LTV, current UPB, delinquency status, and state have no missing values in all
seven processed panels. FICO missingness is 0.181–3.416% and DTI missingness is
0.004–3.046%. `loan_payment_history` has materially different completeness by
vintage, from 96.117% missing in 2006Q1 to 0.353% in 2022Q1. It will therefore
not be automatically included in one cross-cohort model: first, a comparable
feature version will be built, while history-based features will be examined
separately.

Table: [selected-field missingness](../../reports/eda_v01/02_selected_field_missingness.csv).
Figure: [missingness trend](../../reports/figures/eda_v01/04_selected_field_missingness.png).

## 11.3. Delinquency and labelled outcomes

The share of current loan-months at 90+ DPD varies by cohort: 4.4351% in
2008Q1, 3.4609% in 2006Q1, 0.2629% in 2012Q1, and 0.3441% in 2024Q1. The
highest observed calendar-month share in the combined panels is December 2011:
11.4808% at 30+ DPD and 6.7115% at 90+ DPD. This is a **compositional** trend
of selected cohorts, not a US market-wide estimate, since the active-loan mix
changes over time.

Among eligible, uncensored observations, the six-month formal-adverse outcome
ranges from 0.2306% to 2.6513%, and early deterioration from 1.3531% to
7.0331%. The classes are therefore imbalanced, especially for formal adverse
risk; subsequent model evaluation must use PR-AUC, recall, and calibration in
addition to ROC-AUC.

Tables: [status distribution](../../reports/eda_v01/04_current_delinquency_distribution.csv),
[outcome summary](../../reports/eda_v01/05_six_month_outcome_summary.csv), and
[calendar trend](../../reports/eda_v01/06_calendar_month_delinquency_trend.csv).

Figures: [outcomes by cohort](../../reports/figures/eda_v01/01_six_month_outcome_rates_by_cohort.png),
[status distribution](../../reports/figures/eda_v01/02_current_delinquency_distribution.png),
[origination characteristics](../../reports/figures/eda_v01/03_origination_characteristics_trend.png), and
[calendar trend](../../reports/figures/eda_v01/05_calendar_month_delinquency_trend.png).

## 11.4. Feature-engineering decisions

The baseline cross-cohort set will comprise fields available at time *t*:
origination fields (FICO, DTI, LTV/CLTV, UPB, purpose, occupancy, state, and
others) and current fields (loan age, current UPB, rate, remaining maturity,
and current delinquency status). Loan identifier, Zero Balance fields, outcome
labels, and post-event values are excluded. `loan_payment_history` will enter
only after a separate semantic and completeness assessment; this prevents
technical absence of history from being mistakenly interpreted as a favourable
condition.

The feature list, temporal admissibility, and transformation rules are fixed in
[`fannie_feature_spec_v01.yml`](../../config/fannie_feature_spec_v01.yml).
Stage 12 will create a temporal split without mixing future observations
into the training data.
