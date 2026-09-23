# Research abstract

## Research topic

**“Explainable artificial intelligence for early detection of credit risk and
hidden deterioration in borrower quality.”**

## Abstract

This study examines whether information available for an individual loan at a
reporting month can identify subsequent deterioration in mortgage credit quality
before a formal adverse event is observed. The empirical analysis uses the
Fannie Mae Single-Family Loan Performance Primary Dataset and treats a
loan-month as the unit of analysis. Model development, calibration, and final
assessment are separated chronologically. Predictions are therefore evaluated
on later, previously unseen periods, and future information is excluded from
the features.

Two six-month outcomes are examined: formal adverse status, defined by a future
90+ days-past-due status, and early deterioration, defined as a transition from
a current status to 30+ days past due. Logistic regression provides an
interpretable benchmark and XGBoost a nonlinear comparison. Alongside
discrimination metrics, the study evaluates probability calibration,
capacity-constrained alert thresholds, and lead time. TreeSHAP describes the
model's reliance on observed variables and is not interpreted causally.

Within the selected Fannie Mae cohorts, XGBoost achieves higher out-of-time
discrimination than the logistic benchmark. The resulting analytical prototype
produces a risk estimate, an explanation of the prediction, and an alert tier
for prioritising expert review. It is not an autonomous credit or supervisory
decision system.
