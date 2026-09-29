# 29. Macro-enriched experiment protocol

## Purpose and status

This protocol defines a separate experiment testing whether macroeconomic and
regional context that was available at scoring time changes prediction quality
for `formal_adverse_6m` and `early_deterioration_6m`. At the time of protocol
lock, this is not a research result: the mart has not been joined to the
samples and no models have been retrained. The v01 and v02 results therefore
remain the baselines.

## Comparable design

Baseline and macro-enriched variants use the same `model_samples_v01` split:
January 2006–December 2016 for training, January 2017–December 2020 for
validation, and January 2021–September 2025 for independent out-of-time
testing. Hyperparameters and calibration are selected on validation only; the
OOT sample is reserved for one final evaluation.

XGBoost v01 remains the immutable comparison point. XGBoost, LightGBM, and
CatBoost will be assessed in the macro-enriched branch. The candidate is
selected by validation PR-AUC with ROC-AUC and Brier score as guardrails; this
selection rule is fixed before fitting.

## Point-in-time mart

The mart is built from ALFRED vintage snapshots at `monthly_reporting_period`.
It includes the effective federal funds rate, US unemployment, state
unemployment, and state FHFA HPI. Each record retains the series identifier,
requested vintage date, source observation date, and retrieval time. These
fields permit verification that neither a value published later nor a later
revision entered a score-time feature vector.

Regional values join on `property_state`. The samples cover the 50 states, DC,
GU, PR, and VI. Where a regional series is unavailable for a territory on a
given score date, the value remains missing and only an explicit availability
indicator may be supplied to the model. Replacing it with a state average is
not permitted.

## Pre-fitting gates

Four conditions precede fitting: (1) an audit of mart coverage by month,
geography, and series; (2) confirmation that observation and vintage dates do
not follow the score date; (3) a frozen eligible-feature list; and (4) a saved
manifest, seed, and configuration for every run. Only then are ROC-AUC,
PR-AUC, Brier score, calibration, Red/Amber alert performance, lead time, and
queue volume calculated.
