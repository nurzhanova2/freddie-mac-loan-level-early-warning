# Appendix B. Data lineage and working glossary

## B.1. Purpose and scope

This appendix documents the path from the archived source delivery to the
reproducible research artifacts. It does not replace the official Fannie Mae
[file layout and glossary](../../sources/crt-file-layout-and-glossary.xlsx),
which remains the authority for field names, codes, and types. It contains only
concepts used in the analytical workflow and research prototype; individual loan
records are not disclosed.

## B.2. Data lineage

```text
Fannie Mae Primary Dataset archive
        ↓  structural, key, and SHA-256 checks
raw ZIP / manifests
        ↓  type and date cleaning; missing-value normalisation
cleaned 113-field layer
        ↓  fields available as of t and 35-field analytical panel
loan–month panel
        ↓  future windows, censoring, and 3/6/12-month outcomes
labelled analytical panels
        ↓  temporal train / validation / OOT separation
versioned model samples and manifests
        ↓  models, validation-only calibration, fixed queue policies
metrics, SHAP, permutation importance, ALE, and figures
        ↓  safe score export without raw loan-level fields
research SupTech prototype
```

Each transition retains an input version, configuration, and output artifact.
Source archives and panels remain inside the research environment. The browser
layer receives only an approved alert DTO: a pseudonymous case reference,
assessment date, score, alert tier, model version, concise local explanation,
expert-review status, and—after the outcome window closes—the observed outcome.
It does not receive a raw archive, a Fannie Mae loan identifier, or a full
feature vector.

| Layer | Primary function | Reproducibility control |
|---|---|---|
| Raw | retain source delivery | manifest and SHA-256; no overwrite |
| Interim | technically cleaned record | field count, loan–month keys, types |
| Processed | as-of-date analytical panel | leakage register and outcome version |
| Model samples | temporal train/validation/OOT subsets | seed, hash rule, manifest |
| Reports | metrics, calibration, XAI, figures | model and configuration version |
| Prototype export | safe alert view | field allow-list and export version |

## B.3. Working glossary

| Term / field | Meaning in this study | Use |
|---|---|---|
| Cohort / vintage | loan-origination quarter, e.g. `2008Q1` | stratification and robustness |
| Observation month | month when a prediction is formed | time *t* and availability boundary |
| Loan–month | a loan-month record | unit of analysis |
| Current delinquency status | servicing status at time *t* | risk set and features |
| Formal adverse | future 90+ days-past-due status | `formal_adverse_hm` outcome |
| Early deterioration | current-to-30+ DPD transition | `early_deterioration_hm` outcome |
| Horizon | future months searched for an event | 3, 6, or 12; six is primary |
| Censoring | incomplete window or unobserved status | not a non-event |
| Leakage | information unavailable at time *t* | excluded before training/evaluation |
| Zero Balance Code / Effective Date | loan-termination information | checks/outcomes, not predictors |
| Train / validation / OOT | fitting, calibration, assessment periods | 2006–2016 / 2017–2020 / 2021–2025, v01 |
| Calibration | align score and observed event frequency | isotonic regression, validation only |
| Red alert | top-1% `formal_adverse_6m` queue | priority expert review |
| Amber alert | top-5% `early_deterioration_6m` queue | monitoring alert |
| Lead time | months between alert and event | operational characteristic |
| SHAP | feature contribution to a model score | model behaviour, not a causal effect |
| Permutation importance | performance loss after feature permutation | global-importance check |
| ALE | averaged feature–score dependence profile | dependency-shape check |

## B.4. Link to the methodological audit

Outcome definitions, censoring, actual training samples, model settings,
calibration, and Red/Amber policy are specified in [Appendix A](appendix_a_methodological_audit.md).
Field-exclusion decisions are recorded in the [leakage register](../../../data/dictionaries/fannie_2008q1_leakage_register_v01.csv),
and the unified evidence numbering is maintained in the [list of tables and
figures](list_of_tables_and_figures.md).
