# Stages 8–11. Comparison of 3-, 6-, and 12-month horizons

## Protocol

Separate 3-, 6-, and 12-month labels were constructed for each outcome using
common risk-set and censoring rules. Six XGBoost models were fitted on
deterministic 1% natural-rate training samples from 2006–2016; isotonic
calibrators were fitted only on the 2017–2020 validation period. The common OOT
interval is January 2021–March 2025 because it is the latest period with a
complete 12-month future window in data available through March 2026. Model
manifests were locked after OOT assessment.

Absolute PR-AUC, Brier score, and precision are not directly comparable across
horizons because outcome prevalence increases as the future window expands.
The analysis therefore reports ROC-AUC alongside PR lift (PR-AUC divided by
event prevalence), precision lift, and Brier skill score against a constant
prevalence forecast.

## Formal adverse

| Horizon | Event rate, % | ROC-AUC | PR-AUC | PR lift | Brier skill | Red precision, % | Precision lift | Mean lead time, months |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 3 | 0.266565 | 0.938444 | 0.375315 | 140.797 | 0.257 | 20.362 | 76.385 | 1.711 |
| 6 | 0.495222 | 0.871818 | 0.293840 | 59.335 | 0.186 | 25.223 | 50.932 | 2.334 |
| 12 | 0.928151 | 0.846222 | 0.235022 | 25.322 | 0.116 | 29.756 | 32.059 | 3.678 |

For formal adverse, discrimination declines consistently as the horizon grows:
ROC-AUC falls by 0.092222 between three and twelve months, and PR lift falls
from 140.797 to 25.322. Rising absolute Red precision does not imply better
ranking because the base event rate more than triples; precision lift declines.
The longer horizon increases lead time but weakens event/non-event separation.

## Early deterioration

| Horizon | Event rate, % | ROC-AUC | PR-AUC | PR lift | Brier skill | Amber precision, % | Precision lift | Mean lead time, months |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 3 | 1.297300 | 0.726818 | 0.035236 | 2.716 | 0.009 | 5.002 | 3.856 | 1.849 |
| 6 | 2.327492 | 0.726690 | 0.062342 | 2.679 | 0.015 | 8.700 | 3.738 | 3.082 |
| 12 | 4.148883 | 0.717588 | 0.098336 | 2.370 | 0.020 | 13.629 | 3.285 | 5.347 |

For early deterioration, ROC-AUC changes little from three to six months but
falls to 0.717588 at twelve months. PR lift and precision lift decline across
the three horizons. Brier skill remains low at every horizon and does not
support calling the 12-month model superior: it measures probability error
against a changing base rate, while discrimination and queue prioritisation
weaken.

## Conclusion

The hypothesis of unchanged quality at longer horizons is not supported in this
sample. Three-month models provide the strongest discrimination but the least
time to act; twelve-month models provide earlier signals with weaker risk
ranking. Six months remains a defensible operational compromise: mean lead time
is 2.334 months for formal adverse and 3.082 months for early deterioration,
while ROC-AUC and prevalence-adjusted PR-AUC exceed their 12-month values.

## Artefacts

- [primary OOT metrics](../../reports/horizon_sensitivity_v01/horizon_oot_metrics_summary_v01.csv);
- [prevalence-adjusted comparison](../../reports/horizon_sensitivity_v01/horizon_oot_comparability_summary_v01.csv);
- [formal-adverse figure](../../reports/figures/horizon_sensitivity_v01/formal_adverse_horizon_oot_comparability_v01.png);
- [early-deterioration figure](../../reports/figures/horizon_sensitivity_v01/early_deterioration_horizon_oot_comparability_v01.png).
