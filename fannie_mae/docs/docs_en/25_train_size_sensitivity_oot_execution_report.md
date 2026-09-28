# Stages 5–7. Independent OOT evaluation of training-size sensitivity

## Evaluation design

The eight models fixed in Stages 1–4 were applied once to the unchanged Q1
out-of-time sample from January 2021 to September 2025. It contains 658,314
observations and 3,192 formal-adverse events, and 651,914 observations and
15,242 early-deterioration events. Neither models nor isotonic calibrators were
refitted after OOT evaluation began. The technical contract is recorded in the
[configuration](../../config/fannie_train_size_sensitivity_evaluation_v01.yml).

The Red queue was pre-defined as the top 1% of calibrated scores for
`formal_adverse_6m`; the Amber queue was pre-defined as the top 5% for
`early_deterioration_6m`. This is a review-capacity policy, not an OOT-tuned
numeric threshold: each new scoring batch is ranked and a fixed proportion is
sent to review.

## Formal-adverse results

| Train, % | ROC-AUC (raw) | PR-AUC (raw) | Calibrated Brier | Red precision, % | Red recall, % | Alerts | Mean lead time, months |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 0.878769 | 0.273870 | 0.004034 | 24.836701 | 51.221805 | 6,583 | 2.480 |
| 5 | 0.887888 | 0.277149 | 0.004151 | 24.213884 | 49.937343 | 6,583 | 2.459 |
| 10 | 0.891089 | 0.272254 | 0.004164 | 24.137931 | 49.780702 | 6,583 | 2.458 |
| 25 | 0.892613 | 0.276841 | 0.004146 | 24.031597 | 49.561404 | 6,583 | 2.480 |

ROC-AUC increases from 0.878769 to 0.892613, but the remaining measures do
not improve monotonically. The 1% sample has the lowest Brier score and the
highest Red precision and recall; at 25%, precision is lower by 0.805 percentage
points and recall by 1.660 percentage points. Mean lead time lies in the narrow
2.458–2.480-month range. Without confidence intervals, this pattern is not
interpreted as harm from more data; it indicates no stable operational gain at
the tested shares.

## Early-deterioration results

| Train, % | ROC-AUC (raw) | PR-AUC (raw) | Calibrated Brier | Amber precision, % | Amber recall, % | Alerts | Mean lead time, months |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 0.727414 | 0.065016 | 0.022471 | 8.813965 | 18.849232 | 32,596 | 3.020 |
| 5 | 0.730062 | 0.064268 | 0.022570 | 8.448889 | 18.068495 | 32,596 | 3.009 |
| 10 | 0.730470 | 0.063962 | 0.022558 | 8.439686 | 18.048812 | 32,596 | 3.017 |
| 25 | 0.730870 | 0.064193 | 0.022545 | 8.436618 | 18.042252 | 32,596 | 2.999 |

For early deterioration, the raw ROC-AUC gain between 1% and 25% is 0.003456.
The 1% sample nevertheless has the lowest Brier score and the highest Amber
precision and recall; mean lead time varies by no more than 0.021 months.
Thus, on this temporal test, enlarging training data beyond 1% does not yield a
practically material improvement at fixed Amber capacity.

## Saturation and practical implication

Within the natural Q1 training period, 1% corresponds to 622,812 observations
for formal adverse and 609,823 for early deterioration. Across the tested
range, it is the smallest size that retains competitive discrimination, the
best Brier score, and the highest precision for the fixed review queues. It is
therefore a resource-efficient candidate for research retraining of the
SupTech prototype.

This conclusion concerns one deterministic sample and one Q1 OOT period. It
does not establish a universal minimum historical-data requirement and does not
replace external validation. Before operational use, the sample size should be
confirmed on Q3 controls, on harmonised Freddie Mac data, and preferably on
several independent temporal slices.

## Artefacts

- [OOT metrics summary](../../reports/train_size_sensitivity_v01/train_size_oot_metrics_summary_v01.csv);
- [formal-adverse metrics by training size](../../reports/train_size_sensitivity_v01/formal_adverse_6m_train_size_oot_metrics_v01.csv);
- [early-deterioration metrics by training size](../../reports/train_size_sensitivity_v01/early_deterioration_6m_train_size_oot_metrics_v01.csv);
- **Figure 4.4**: [formal-adverse training size and OOT metrics](../../reports/figures/train_size_sensitivity_v01/formal_adverse_6m_train_size_oot_metrics_v01.png);
- **Figure 4.5**: [early-deterioration training size and OOT metrics](../../reports/figures/train_size_sensitivity_v01/early_deterioration_6m_train_size_oot_metrics_v01.png);
- **Figure 4.6**: [formal-adverse OOT reliability](../../reports/figures/train_size_sensitivity_v01/formal_adverse_6m_train_size_oot_calibration_v01.png);
- **Figure 4.7**: [early-deterioration OOT reliability](../../reports/figures/train_size_sensitivity_v01/early_deterioration_6m_train_size_oot_calibration_v01.png);
- [OOT evaluation script](../../../src/fannie_mae/evaluate_fannie_natural_train_size_oot.py).
