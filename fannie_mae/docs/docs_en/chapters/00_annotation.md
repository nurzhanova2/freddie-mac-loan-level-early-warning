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

Within the selected Fannie Mae cohorts, XGBoost achieves higher out-of-time
ranking performance than logistic regression. The practical output is an
analytical prototype that produces a risk estimate, an explanation, and an
alert tier for expert review. It neither replaces nor automates credit or
supervisory decisions.
