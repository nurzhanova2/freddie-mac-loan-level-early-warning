# Chapter 4. Early-warning modelling and temporal validation

## 4.1. Modelling rationale

The empirical comparison is centred on logistic regression and XGBoost.
Logistic regression provides a transparent reference against which the
incremental value of nonlinear interactions can be assessed; this benchmark
design follows the empirical comparison tradition in credit scoring [51].
XGBoost is included as a scalable gradient-boosting implementation [61], since
the relationship between loan characteristics, payment status, and subsequent
deterioration need not be linear. Superior predictive performance is not
interpreted as evidence of a causal relationship between a feature and an
outcome.

## 4.2. Temporal validation design

To reflect the prospective use of an early-warning model, observations are
partitioned only by calendar time: January 2006–December 2016 for training,
January 2017–December 2020 for validation, and January 2021–September 2025 for
the independent out-of-time test. September 2025 is the latest admissible
prediction month because the source ends in March 2026 and a complete
six-month outcome window is required. The design is shown in **Figure 4.1** —
[“Chronological split”](../../../reports/figures/splits/fannie_temporal_split_timeline_v01.png).
Temporal rather than random splitting is consistent with dynamic credit-scoring
approaches [6], [53].

All transformations, feature selection, sampling decisions, and calibration
mapping are estimated without access to the out-of-time period. The loan
identifier is retained solely for linkage and audit, not as a predictor. Thus,
repeated monthly observations of the same loan are consistent with the intended
dynamic-monitoring setting and do not expose the model to the identifier or to
future-month values. The resulting sample composition is reported in
**Table 4.1** — [“Temporal-split summary”](../../../reports/splits/fannie_temporal_split_v01_summary.csv).

## 4.3. Evaluation criteria

ROC-AUC and PR-AUC assess ranking performance, whereas calibration assesses
whether predicted probabilities correspond to observed frequencies. For a binary
outcome $y_i \in \{0,1\}$, the Brier score is
$\operatorname{BS}=\frac{1}{n}\sum_{i=1}^{n}(y_i-\hat{p}_i)^2$; lower values
indicate smaller squared probability errors [62]. Alert thresholds are
additionally evaluated by precision, recall, false-positive burden, and lead
time, since a high-ranking model is not by itself sufficient to define a review
policy.

## 4.4. Data volume and actual training samples

The extended Q1+Q3 workstream contains 467,638,404 loan-month observations and
8,272,539 loans counted across separate cohort panels. The full data volume is
used for panel construction, outcome derivation, descriptive analysis, and the
creation of deterministic samples; it is not loaded into memory as one training
matrix.

For formal adverse status, the case-control training sample contains 1,262,399
observations, including 420,588 events; the validation and independent
out-of-time samples contain 1,034,605 and 1,748,449 observations at natural
event rates. For early deterioration, the corresponding volumes are 1,240,046
(396,152 events), 1,022,461, and 1,732,763 observations. Samples are formed
through a reproducible deterministic hash rule; calibration uses validation
only, and final assessment uses the out-of-time period only. Separate
estimation and calibration of probabilities are important because good ranking
alone does not guarantee a valid probability interpretation [63].

Relative to the full pooled Q1+Q3 panel, the actual training samples represent
approximately 0.270% for formal adverse status and 0.265% for early
deterioration. These figures describe only a volume ratio; they are not simple
random-sampling fractions. The denominator includes every period of the full
panel whereas the training data are confined to the training interval, and the
case-control procedure intentionally enriches rare events. It would therefore
be incorrect to describe the design as a random 0.27% sample. The design
provides computational feasibility, reproducibility, and sufficient target
events, while validation and out-of-time evaluation retain natural event rates.

## 4.5. Protocol for training-size sensitivity analysis

Increasing the training volume does not imply automatically retraining every
candidate algorithm. After a leading model is selected by a pre-specified rule
— PR-AUC first, then Brier score and ROC-AUC on the independent temporal period
— the scale analysis will be conducted only for that model and separately for
each outcome. For formal adverse status, XGBoost is the initial candidate
because it provides the strongest combination of these metrics in the completed
comparison.

The future experiment will use several increasing deterministic case-control
training samples formed only within the training period. All variants will keep
the same temporal boundaries, validation set, and out-of-time test, and will
be compared by ROC-AUC, PR-AUC, Brier score, trigger precision/recall, and lead
time. Any sampling fraction in this analysis will be calculated relative to the
eligible training-period population, rather than all 467,638,404 observations.
Until executed, this procedure is a pre-specified validation plan, not an
empirical result.

## 4.6. Empirical model results

The logistic benchmark obtains out-of-time ROC-AUC values of 0.8794 for formal
adverse status and 0.7254 for early deterioration. Isotonic calibration reduces
its Brier score from 0.021646 to 0.004320 for formal adverse status and from
0.059429 to 0.022507 for early deterioration. These results establish a
calibrated linear reference rather than a final model selection. They are
reported in **Table 4.2** — [“Logistic baseline”](../../../reports/models/logistic_baseline_v01_summary.csv),
**Table 4.3** — [“Calibration summary”](../../../reports/models/logistic_isotonic_calibration_v01_summary.csv),
and **Figure 4.2** — [“Formal-adverse reliability”](../../../reports/figures/models/formal_adverse_6m_calibration_v01.png).
Calibration for early deterioration is shown in **Figure 4.3** —
[“Early-deterioration reliability”](../../../reports/figures/models/early_deterioration_6m_calibration_v01.png).

On the independent out-of-time period, XGBoost yields ROC-AUC of 0.8943 and
PR-AUC of 0.2866 for formal adverse status, and 0.7310 and 0.0663 for early
deterioration. The numerical comparison is presented in [Table 6.1](../../../reports/models/final_model_comparison_v01.csv).
The results support the use of XGBoost as the leading model in this empirical
sample; the scope of that conclusion is considered in Chapter 6.
