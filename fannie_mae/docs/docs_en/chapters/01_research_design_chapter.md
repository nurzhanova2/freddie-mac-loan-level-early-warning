# Chapter 1. Research concept and design

## 1.1. Research problem

Mortgage-credit deterioration may be visible in monthly servicing data before a
loan reaches the 90+ days-past-due threshold used here as a formal adverse
outcome. The research problem is therefore to identify loan-month observations
that warrant earlier expert attention using only information available at the
reporting month. The study addresses this problem with an explainable loan-level
predictive model for the U.S. single-family mortgage segment.

## 1.2. Aim, subject and working hypothesis

The aim is to develop and evaluate a reproducible procedure for estimating the
risk of subsequent mortgage-credit deterioration. This formulation follows
dynamic credit-scoring research, in which risk changes over time rather than
being treated as an immutable loan attribute [6], [52], [53]. The subject of
the study is the relationship between information available at the observation
date and a future six-month deterioration outcome.

The working hypothesis is that a model evaluated on later periods can provide
informative early-warning signals. Explanation methods are used to audit the
associations on which the model relies; they do not identify causal mechanisms
[54], [55].

## 1.3. Research design

The research procedure follows the sequence

`data → risk estimate → deterioration signal → explanation → alert tier → expert review`.

This sequence separates prediction from decision-making. The model ranks
observations by estimated risk, and a pre-specified threshold selects the cases
for review. Performance is assessed through discrimination, probability
calibration, alert precision and recall, lead time, and temporal stability.
Fannie Mae and Freddie Mac are retained as separate empirical workstreams:
their field structures and data-generating processes are not assumed to be
interchangeable without separate harmonisation.

The extended design tests whether findings obtained from Q1 cohorts remain
stable when the origination quarter changes. Q3 cohorts are consequently used
as an independent control population rather than as additional training volume.
They include the pre-crisis `2006Q3` cohort, the acute-crisis `2008Q3` cohort,
the recovery-period `2012Q3` cohort, the pandemic-period `2020Q3` cohort, the
rising-rate `2022Q3` cohort, and the recent-market `2024Q3` cohort; other
available Q3 cohorts retain temporal continuity. The comparison tests robustness
to origination quarter, not a causal role of historical periods. The 2007–09
crisis and subsequent recovery are documented in [58], the pandemic business-
cycle turning point in [59], and the 2022 monetary-policy tightening in [60].

## 1.4. Dissertation structure

Chapter 2 defines the empirical sample and data-quality procedures. Chapter 3
sets out outcomes, admissible predictors, and information-leakage controls.
Chapter 4 covers modelling, calibration, and temporal validation. Chapter 5
examines explainability and model-risk governance. Chapter 6 interprets the
results within the stated scope of the study.
