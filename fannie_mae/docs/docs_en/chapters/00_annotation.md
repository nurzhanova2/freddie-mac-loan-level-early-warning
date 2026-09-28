# Research abstract

## Research topic

**“Explainable artificial intelligence for early detection of credit risk and
hidden deterioration in borrower quality.”**

## Abstract

This study examines whether information available for an individual mortgage at
a reporting month can identify subsequent deterioration in credit quality before
a formal adverse event is observed. The empirical analysis uses the Fannie Mae
Single-Family Loan Performance Primary Dataset and treats a loan-month as the
unit of analysis. Model development, probability calibration, and final
assessment are separated chronologically. Predictions are therefore evaluated
on later periods not used in model development, while features are limited to
information available at the prediction date.

Two six-month outcomes are considered. Formal adverse status denotes a future
90+ days-past-due status, whereas early deterioration denotes a transition from
a current status to 30+ days past due. Logistic regression provides an
interpretable benchmark, and XGBoost supplies the nonlinear comparison. The
evaluation covers ranking performance, probability calibration,
capacity-constrained alert thresholds, and lead time. TreeSHAP is used to
describe the contribution of observed features to predictions; it is not given
a causal interpretation.

On the independent out-of-time period, XGBoost reaches ROC-AUC 0.8943 and
PR-AUC 0.2866 for formal adverse, and 0.7310 and 0.0663 for early deterioration.
The top-1% Red policy identifies 50.09% of formal-adverse events at 24.29%
precision and mean lead time of 2.467 months. The practical output is an
analytical prototype that produces a risk estimate, an explanation, and an
alert tier for expert review. It neither replaces nor automates credit or
supervisory decisions.
