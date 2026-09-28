# Chapter 6. Results, discussion and conclusions

## 6.1. Interpretation of predictive results

The empirical sample comprises 3,343,420 loans and 185,931,842 loan-month
observations. On the independent out-of-time period, XGBoost obtains ROC-AUC
of 0.8943 and PR-AUC of 0.2866 for formal adverse status, compared with 0.8794
and 0.1879 for logistic regression. For early deterioration, the corresponding
values are 0.7310 and 0.0663 for XGBoost, versus 0.7254 and 0.0596 for the
benchmark. The complete comparison is reported in [Table 6.1](../../../reports/models/final_model_comparison_v01.csv).

The improvement supports nonlinear modelling in this sample, particularly for
the rarer formal-adverse outcome. It remains an empirical comparison within one
information set rather than evidence of a universal algorithmic advantage [1].
The estimated relationships need not reproduce unchanged in other mortgage
populations or future economic conditions.

## 6.2. Interpretation of alert policies

At a top-1% review capacity, the formal-adverse policy identifies 50.09% of
events at 24.29% precision and a mean lead time of 2.467 months. At a top-5%
capacity, the early-deterioration policy has 8.69% precision, 18.59% recall,
and a mean lead time of 2.993 months. These results describe the trade-off
between coverage and review burden: the first tier forms a concentrated priority
queue, while the second supplies a broader monitoring signal for expert review.
They do not measure the economic effect of any intervention.

The model and trigger results are summarised in **Figure 6.1** — [“Model and trigger summary”](../../../reports/figures/final_v01/final_model_and_trigger_summary_v01.png)
and **Table 6.2** — [“Final study metrics”](../../../reports/models/final_dissertation_summary_v01.csv).

### 6.2.1. Historical-data volume for research retraining

An additional experiment using Q1 natural-rate samples tests whether the
SupTech prototype requires substantially more historical data while retaining
the same temporal boundaries, calibrator, and queue capacities. Within the
tested range, 1% of train corresponds to 622,812 observations for formal
adverse and 609,823 for early deterioration. On OOT, this smallest size yields
a Brier score of 0.004034 and Red precision of 24.84% for formal adverse, and
a Brier score of 0.022471 and Amber precision of 8.81% for early deterioration.
Increasing the share to 25% improves raw ROC-AUC but does not consistently
improve PR-AUC, calibration, or queue precision.

Accordingly, 1% natural-rate train is a resource-efficient candidate for
research retraining within this contour. This does not imply that additional
history harms performance or that a universal minimum data volume has been
established: the conclusion relies on one deterministic Q1 selection and
requires confirmation on independent Q3 and Freddie Mac data. Detailed results
appear in [Table 4.4](../../../reports/train_size_sensitivity_v01/train_size_oot_metrics_summary_v01.csv)
and [Figures 4.4–4.7](../25_train_size_sensitivity_oot_execution_report.md).

### 6.2.2. Trade-off between horizon and time to act

The horizon comparison confirms the expected trade-off in this sample.
Three-month formal-adverse ROC-AUC is 0.938444, compared with 0.846222 at
twelve months; early-deterioration values are 0.726818 and 0.717588. Mean lead
time nevertheless rises from 1.711 to 3.678 months for formal adverse and from
1.849 to 5.347 months for early deterioration. The six-month horizon retains
stronger ranking than the twelve-month horizon while leaving 2.334 and 3.082
months for expert response. It therefore remains the prototype's principal
operational horizon; three and twelve months are short- and long-horizon
sensitivity analyses rather than replacements for the Red/Amber policy.

The rise in absolute precision at twelve months does not change that
interpretation. A longer window includes more future events, so formal-adverse
prevalence rises from 0.266565% to 0.928151% and Red precision rises from
20.362% to 29.756%. Precision lift simultaneously falls from 76.385 to 32.059.
For early deterioration, Amber precision rises from 5.002% to 13.629% while
its lift falls from 3.856 to 3.285. Thus, the increase in absolute precision
at twelve months is principally a higher-base-rate effect, not evidence of
superior prioritisation.

## 6.3. Limitations and further research

The conclusions are limited to the Fannie Mae Primary Dataset and seven Q1
acquisition cohorts. Application to Freddie Mac requires independent
harmonisation of fields and outcomes. Models were trained on reproducible,
deterministic case-control samples; calibration and final assessment used
temporal samples with natural outcome rates. Observed associations and SHAP
values are not causal estimates [25], [2]. Further cohorts, including
non-Q1 originations, are needed to assess sensitivity to acquisition season.

Fannie Mae remains the only source for the principal evaluation. The findings
describe conventional, fully-amortising fixed-rate mortgages and cannot be
automatically transferred to other market segments. Q3 testing examines
robustness within available cohorts but does not replace external validation on
Freddie Mac after harmonising fields, status codes, outcome horizons, and
censoring rules. Macroeconomic indicators, regional house prices, and local
market conditions were not used as predictors [39]. SHAP describes model
behaviour, and threshold metrics do not measure the effect of expert or
supervisory intervention.

Further work includes independent Freddie Mac validation with a pre-specified
field crosswalk and immutable evaluation protocol; broader Q1–Q4 coverage;
testing the incremental value of predictors available at the prediction date;
and prospective backtesting with drift monitoring, recalibration, and
retraining rules [2], [46]. The research-prototype interface should also be
evaluated for usability, workload, and its effect on human decision-making.

## 6.4. Key empirical conclusions

1. XGBoost for `formal_adverse_6m` obtains ROC-AUC 0.8943 and PR-AUC 0.2866,
   exceeding logistic regression by 0.0149 and 0.0987, respectively.
2. For `early_deterioration_6m`, XGBoost improves ROC-AUC by 0.0056 and PR-AUC
   by 0.0066; this more frequent outcome remains harder to prioritise.
3. Isotonic calibration reduces the logistic model's Brier score from 0.021646
   to 0.004320 for formal adverse and from 0.059429 to 0.022507 for early
   deterioration.
4. The top-1% Red policy identifies 50.09% of formal-adverse events at 24.29%
   precision and mean lead time of 2.467 months.
5. The top-5% Amber policy has 8.69% precision, 18.59% recall, and mean lead
   time of 2.993 months; it is a monitoring instrument, not an autonomous
   decision.
6. The Q1/Q3 explanation-transferability test yields SHAP rank correlations of
   0.9962 for formal adverse and 0.9938 for early deterioration, with top-ten
   feature overlap of 10 and 9.
7. In the sensitivity analysis, 1% of the natural Q1 training population —
   622,812 and 609,823 observations across the two outcomes — retains
   competitive OOT metrics and the highest fixed-queue precision. This
   resource benchmark requires independent confirmation and is not a universal
   threshold.
8. With a common OOT window, three-month models provide the strongest ranking
   and twelve-month models the greatest lead time. The six-month horizon
   retains higher ROC-AUC and prevalence-adjusted PR-AUC than the twelve-month
   horizon while allowing 2.334–3.082 months for expert response.

Consolidated artefacts and the full audit specification are provided in
[Appendix A](../appendices/appendix_a_methodological_audit.md) and the
[list of tables and figures](../appendices/list_of_tables_and_figures.md).

## 6.5. Practical value of the SupTech-inspired prototype

The practical output is a research SupTech-inspired prototype, not a deployed
supervisory information system. Its logic is

`data → risk score → alert → local explanation → risk trigger → expert review`.

Monthly servicing records are converted into admissible predictors, after which
the calibrated model estimates the probability of future deterioration. The
threshold policy maps that probability to a Red or Amber alert at a specified
review capacity. Each alert retains a local SHAP explanation and its data,
model, and threshold version, allowing an expert to assess the case outside the
model. The prototype does not provide automated loan denial, sanctions, or
supervisory intervention.

## 6.6. Conclusion

Within the stated empirical scope, the working hypothesis receives support:
an explainable loan-month model evaluated on future periods can produce early
risk signals with measurable discrimination, calibrated probabilities, and
limited lead time. The principal contribution is the reproducible integration
of temporal validation, leakage control, probability calibration, threshold
policy, and explanation into one analytical procedure for expert review.
Explainability and documentation complement, but do not replace, independent
validation of a credit-risk model [28], [2], [46].
