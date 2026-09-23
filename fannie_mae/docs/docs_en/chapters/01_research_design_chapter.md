# Chapter 1. Research concept and design

## 1.1. Research problem

Mortgage-credit deterioration may become observable in monthly servicing data
before it reaches the 90+ days-past-due threshold used here as a formal adverse
outcome. The research problem is therefore to identify loan-month observations
that warrant earlier expert attention using only information available at the
reporting month. The study addresses this problem through an explainable
loan-level predictive model for the U.S. single-family mortgage segment.

## 1.2. Aim, subject and working hypothesis

The aim is to develop and evaluate a reproducible procedure for estimating the
risk of subsequent mortgage-credit deterioration. This formulation is
consistent with dynamic credit-scoring research, in which risk changes over
time rather than being treated as an immutable loan attribute [6], [52], [53].
Its subject is the
relationship between information available at the observation date and a future
six-month deterioration outcome. The working hypothesis is that a model
validated on later periods can provide practically informative early-warning
signals. Explanation methods are used to audit the model's associations with
input variables; they do not identify causal mechanisms [54], [55].

## 1.3. Research design

The analytical sequence connects the research objective to a review process:

`data → risk estimate → deterioration signal → explanation → alert tier → expert review`.

The sequence separates prediction from decision-making. A model score ranks
observations by estimated risk, while a pre-specified threshold determines
which observations are presented for review. Performance is assessed through
discrimination, probability calibration, alert precision and recall, lead time,
and temporal stability. The Fannie Mae and Freddie Mac sources are maintained
as separate empirical workstreams because their field definitions and data
generation processes are not assumed to be interchangeable.

The methodological contribution of the extension is to examine whether
findings obtained from Q1 cohorts remain stable when the origination quarter
changes. Q3 cohorts are therefore treated as an independent control population,
not merely as additional training volume. They include the pre-crisis period
`2006Q3`, the acute financial-crisis period `2008Q3`, the recovery period
`2012Q3`, the pandemic-period cohort `2020Q3`, the rising-rate period `2022Q3`,
and the recent market regime `2024Q3`; the other available Q3 cohorts preserve
temporal continuity. This comparison distinguishes robustness to the
origination quarter from performance limited to the initially selected Q1
vintages. These historical labels stratify the control test rather than act as
causal variables: the 2007–09 crisis and subsequent recovery are documented in
[58], the pandemic business-cycle turning point in [59], and monetary-policy
tightening in 2022 in [60].

## 1.4. Dissertation structure

Chapter 2 establishes the empirical sample and data-quality controls. Chapter
3 defines the outcomes, admissible predictors, and information-leakage rules.
Chapter 4 describes modelling, calibration, and temporal validation. Chapter
5 examines explainability and model governance. Chapter 6 interprets the
results within the scope and limitations of the study.
