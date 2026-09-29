# Stage 25. Macroeconomic context and user-evaluation protocol

## Macroeconomic context

Macroeconomic variables are separated into an experimental layer and are not
included in the frozen v01/v02 models. The mart contains the effective federal
funds rate, national unemployment, unemployment in the property's state, and
the FHFA state house price index. To avoid temporal leakage, each series is
retrieved from ALFRED with `vintage_date` equal to the scoring month; the mart
retains the series identifier, requested vintage date, observation date, and
retrieval time. A value published or revised after the score date therefore
cannot enter the feature set.

The January 2021 pilot contains 104 records: two national records and 51
state-level unemployment and HPI records for the states and DC. As of 1 January
2021, the latest available FEDFUNDS and UNRATE values refer to November 2020.
This demonstrates that the point-in-time rule uses information known at the
scoring date rather than a present-day revised series.

The complete historical mart requires a separate controlled run: an archived
vintage must be requested for each month and state-level series. Only after
completeness, temporal availability, and property-state merge rules are audited
may an independent temporal experiment compare baseline features with baseline
plus macro features. Until then, macro variables do not change the dissertation
results, calibration, or trigger policy.
The locked protocol for this comparison is set out in
`29_macro_enriched_experiment_protocol.md`.

## SupTech-prototype user evaluation

The prototype records measurable rather than synthetic use indicators: Red and
Amber volumes, pending and reviewed alerts, review actions, the proportion of
alerts with an observed outcome, and an optional 1–5 reviewer rating of local
SHAP-explanation usefulness. The observed outcome is a post-window audit field
and is not supplied to the model as a feature.

A user evaluation has not yet been conducted with participants. Following real
review sessions, the study should record the user's role, session duration,
alerts viewed, decision, comment, and explanation rating. It can then assess
analyst workload, confirmed Red/Amber proportions, mean explanation usefulness,
and the relation between review workflow and known lead time. Until such records
exist, the interface is instrumented for evaluation rather than demonstrated to
be useful to users.
