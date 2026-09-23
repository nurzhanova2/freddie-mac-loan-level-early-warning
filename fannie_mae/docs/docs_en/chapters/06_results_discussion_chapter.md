# Chapter 6. Results, discussion and conclusions

## 6.1. Interpretation of predictive results

The empirical sample comprises 3,343,420 loans and 185,931,842 loan-month
observations. In the independent out-of-time period, XGBoost achieves ROC-AUC
of 0.8943 and PR-AUC of 0.2866 for formal adverse status, compared with 0.8794
and 0.1879 for logistic regression. For early deterioration, the corresponding
XGBoost values are 0.7310 and 0.0663, compared with 0.7254 and 0.0596 for the
benchmark. The complete comparison is reported in [Table 6.1](../../../reports/models/final_model_comparison_v01.csv).

The observed improvement supports the use of nonlinear modelling in this
sample, particularly for the rarer formal-adverse outcome. This result should
be interpreted as an empirical comparison within one information set rather
than as a universal algorithmic advantage; the need for this type of comparison
is emphasised in credit-scoring research [51]. It does not imply
that the estimated relationships will reproduce unchanged in other mortgage
populations or future economic conditions.

## 6.2. Interpretation of alert policies

At a top-1% review capacity, the formal-adverse policy identifies 50.09% of
events with precision of 24.29% and mean lead time of 2.467 months. At a top-5%
capacity, the early-deterioration policy has precision of 8.69%, recall of
18.59%, and mean lead time of 2.993 months. These figures quantify a trade-off:
the former tier is suitable for a concentrated priority queue, whereas the
latter provides a broader monitoring signal that requires expert assessment.
They do not establish the economic benefit of a particular intervention.

The model and trigger results are summarised in **Figure 6.1** —
[“Model and trigger summary”](../../../reports/figures/final_v01/final_model_and_trigger_summary_v01.png)
and **Table 6.2** — [“Final study metrics”](../../../reports/models/final_dissertation_summary_v01.csv).

## 6.3. Limitations

The conclusions are restricted to the Fannie Mae Primary Dataset and seven Q1
acquisition cohorts. Application to Freddie Mac requires an independent
harmonisation of fields and outcomes. Rather than the full record population,
the models were trained on reproducible deterministic case-control samples;
calibration and final evaluation were conducted on temporal samples with natural
outcome rates. Observed associations and SHAP
values are not causal estimates [54], [55]. Additional cohorts, including non-Q1
originations, are required to assess robustness to acquisition-season effects.

First, Fannie Mae is the sole source for the principal evaluation; the findings
describe the documented population of conventional, fully-amortising fixed-rate
mortgages and cannot automatically be transferred to other mortgage segments.
Second, Q3 testing assesses robustness within the available cohorts but does
not replace independent external validation on Freddie Mac after harmonising
fields, status codes, outcome horizons, and censoring rules. Third, the study
uses loan and servicing-history predictors; macroeconomic indicators, regional
house-price measures, and local-market conditions were not included as
predictors [53]. Finally, SHAP describes model behaviour rather than causality, and
threshold metrics do not measure the economic effect of an expert or
supervisory intervention.

### Directions for further research

1. Conduct independent validation on Freddie Mac with a pre-specified field
   crosswalk, harmonised outcome definitions, and an immutable evaluation
   protocol.
2. Extend time coverage with further Q1, Q2, Q3, and Q4 cohorts in order to
   assess origination seasonality, structural change, and robustness after new
   market regimes separately.
3. Test the incremental value of macroeconomic and regional predictors
   available at the prediction date: interest rates, unemployment, house-price
   indices, and borrower-support measures. Their temporal availability must be
   fixed before model training.
4. Perform prospective backtesting on sequential time windows and define rules
   for drift monitoring, recalibration, and retraining in line with model-
   governance principles [55], [56].
5. Implement a research-prototype user interface that presents the Red/Amber
   queue, score, local explanation, model version, and expert-review outcome.
   Its usability, workload implications, and effect on human decisions should
   be evaluated separately.

## 6.4. Key empirical conclusions

1. On the independent out-of-time period, XGBoost for `formal_adverse_6m`
   obtains ROC-AUC of 0.8943 and PR-AUC of 0.2866, exceeding logistic
   regression by 0.0149 and 0.0987, respectively.
2. For `early_deterioration_6m`, the XGBoost advantage is 0.0056 in ROC-AUC
   (0.7310 versus 0.7254) and 0.0066 in PR-AUC (0.0663 versus 0.0596).
   Early deterioration is therefore a more frequent but materially more
   difficult outcome for practical prioritisation.
3. Isotonic calibration reduces the logistic model's Brier score from 0.021646
   to 0.004320 for formal adverse and from 0.059429 to 0.022507 for early
   deterioration.
4. The top-1% Red policy identifies 50.09% of formal-adverse events at 24.29%
   precision and a mean lead time of 2.467 months.
5. The top-5% Amber policy for early deterioration has 8.69% precision, 18.59%
   recall, and mean lead time of 2.993 months; it is a monitoring instrument,
   not an autonomous decision.
6. The Q1/Q3 explanation-transferability check produces SHAP rank correlations
   of 0.9962 for formal adverse and 0.9938 for early deterioration, with top-ten
   feature overlap of 10 and 9, respectively.

The consolidated artefacts and full audit specification are provided in
[Appendix A](../appendices/appendix_a_methodological_audit.md) and the
[list of tables and figures](../appendices/list_of_tables_and_figures.md).

## 6.5. Practical value of the SupTech-inspired prototype

The practical output is a research SupTech-inspired prototype, not a deployed
supervisory information system. Its logic is:

`data → risk score → alert → local explanation → risk trigger → expert review`.

Monthly servicing records are transformed into admissible predictors, after
which the calibrated model produces a probability of future deterioration. The
threshold policy maps the probability to a Red or Amber alert at a pre-specified
review capacity. Each alert retains a local SHAP explanation and the data,
model, and threshold version, enabling an expert to assess the case context and
make a decision outside the model. The prototype does not provide automatic
credit denial, sanctions, or supervisory intervention.

## 6.6. Conclusion

Within the stated empirical scope, the working hypothesis receives support: an
explainable loan-month model evaluated on future periods can generate early
risk signals with measurable discrimination, calibrated probabilities, and
limited lead time. The principal contribution is the reproducible integration
of temporal validation, leakage control, probability calibration, threshold
policy, and explanation into one analytical procedure for expert review. This
framing follows the view that explainability and documentation complement, but
do not replace, independent validation of a credit-risk model [7], [55], [56].
