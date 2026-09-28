# Stages 1–4. Protocol, natural-rate training samples, and model fitting

## Status

The experimental protocol has been fixed, nested natural-rate training samples
have been exported, eight XGBoost models have been fitted, and each model has
received isotonic calibration. Independent out-of-time evaluation was
intentionally not performed at this stage.

## Fixed design

The experiment uses the Q1 v01 contour, preserving Q3 cohorts as an independent
control population for transportability analysis. Training covers January
2006–December 2016; validation covers January 2017–December 2020; the
out-of-time test covers January 2021–September 2025. The XGBoost specification
and isotonic-calibration rule were fixed before training in the [configuration](../../config/fannie_train_size_sensitivity_v01.yml).

## Sampling rule

For each outcome, all observations with a non-null six-month label inside the
training period are eligible. Shares are selected by the deterministic rule
`hash(loan_identifier, monthly_reporting_period) % 10000 < threshold`, with
thresholds 100, 500, 1000, and 2500 for 1%, 5%, 10%, and 25%. The samples are
nested, and the sampling design preserves natural outcome prevalence.

| Outcome | Share | Observations | Events | Event rate, % |
|---|---:|---:|---:|---:|
| Formal adverse | 1% | 622,812 | 7,527 | 1.208551 |
| Formal adverse | 5% | 3,117,481 | 37,882 | 1.215148 |
| Formal adverse | 10% | 6,233,999 | 75,918 | 1.217806 |
| Formal adverse | 25% | 15,576,478 | 190,119 | 1.220552 |
| Early deterioration | 1% | 609,823 | 22,739 | 3.728787 |
| Early deterioration | 5% | 3,052,708 | 114,100 | 3.737665 |
| Early deterioration | 10% | 6,104,158 | 228,859 | 3.749231 |
| Early deterioration | 25% | 15,251,786 | 570,771 | 3.742322 |

All eight files contain train records dated from 2006-01-01 to 2016-12-01.
For every 1% → 5% → 10% → 25% sequence, the number of keys from the smaller
sample missing in the larger sample is zero.

## Model fitting and calibration

A separate XGBoost model was fitted for every outcome and training share using
the pre-specified hyperparameters. An isotonic calibrator was then fitted only
on the unchanged validation sample: 337,541 observations for formal adverse
and 332,693 for early deterioration. No training script opened the out-of-time
file; every one of the eight manifests records `oot_accessed: false`.

The following table is diagnostic. Its calibrated columns use the same
validation sample on which the calibrator was fitted. It is therefore not an
independent performance assessment and is not used to select alert thresholds.
Those decisions remain reserved for a single evaluation of the fixed models on
the OOT sample.

| Outcome | Share | ROC-AUC, raw / calibrated | PR-AUC, raw / calibrated | Brier score, raw / calibrated |
|---|---:|---:|---:|---:|
| Formal adverse | 1% | 0.818667 / 0.819990 | 0.286202 / 0.281154 | 0.009008 / 0.008758 |
| Formal adverse | 5% | 0.829526 / 0.830601 | 0.301949 / 0.290999 | 0.008919 / 0.008674 |
| Formal adverse | 10% | 0.836836 / 0.838317 | 0.302698 / 0.288296 | 0.008874 / 0.008645 |
| Formal adverse | 25% | 0.833439 / 0.834675 | 0.295923 / 0.284629 | 0.008918 / 0.008672 |
| Early deterioration | 1% | 0.741749 / 0.742540 | 0.100757 / 0.098418 | 0.028382 / 0.028229 |
| Early deterioration | 5% | 0.743849 / 0.744701 | 0.104512 / 0.102058 | 0.028349 / 0.028170 |
| Early deterioration | 10% | 0.745371 / 0.746282 | 0.103768 / 0.101643 | 0.028344 / 0.028178 |
| Early deterioration | 25% | 0.744004 / 0.744893 | 0.104099 / 0.101256 | 0.028344 / 0.028172 |

Eight pairs of `model.joblib` and `isotonic_calibrator.joblib` artefacts have
been saved under `fannie_mae/models/train_size_sensitivity_v01/`. Stages 1–4
do not select a leading training-sample size, calibrate Red/Amber thresholds,
or evaluate OOT metrics. Those actions belong to the next pre-separated stage.

## Artefacts

- [configuration](../../config/fannie_train_size_sensitivity_v01.yml);
- [export script](../../../src/fannie_mae/export_fannie_natural_train_size_samples.py);
- [training script](../../../src/fannie_mae/train_fannie_natural_xgboost_scale.py);
- [formal-adverse manifest](../../data/train_size_sensitivity_v01/formal_adverse_6m_natural_train_size_manifest_v01.csv);
- [early-deterioration manifest](../../data/train_size_sensitivity_v01/early_deterioration_6m_natural_train_size_manifest_v01.csv);
- [model and calibrator artefacts](../../models/train_size_sensitivity_v01/).
