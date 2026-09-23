# Chapter 2. Construction and preparation of the Fannie Mae dataset

## 2.1. Data source and empirical scope

The empirical basis is the Fannie Mae Single-Family Loan Performance Primary
Dataset, distributed through the Data Dynamics platform [57]. It contains
origination characteristics and subsequent monthly servicing records. The study
covers the `2006Q1`, `2008Q1`, `2012Q1`, `2016Q1`, `2020Q1`, `2022Q1`, and
`2024Q1` acquisition cohorts. The analysis is confined to the Primary Dataset;
HARP, multifamily, and Freddie Mac data are not pooled because each requires
separate definitions and processing rules.

The source population consists of conventional, fully amortising,
full-documentation, fixed-rate mortgages with an original term of no more than
30 years. The findings therefore concern this defined population and cannot be
automatically generalised to all U.S. mortgages. The seven panels contain
185,931,842 loan-month observations and 3,343,420 loans. Cohort coverage and
origination characteristics are reported in **Tables 2.1–2.2** — [“Cohort coverage”](../../../reports/eda_v01/01_cohort_overview.csv)
and [“Origination characteristics”](../../../reports/eda_v01/03_origination_characteristics.csv) —
and in **Figure 2.1** — [“Characteristics by cohort”](../../../reports/figures/eda_v01/03_origination_characteristics_trend.png).

## 2.2. Observational structure

The unit of analysis is a loan-month pair. The resulting longitudinal panel is
unbalanced because loans contribute different numbers of monthly observations.
This structure matches the monitoring task: a risk estimate is updated as new
servicing information becomes available.

The initial 2008Q1 delivery contains 22,415,219 records and 380,832 loans from
January 2008 through March 2026. An external-sort audit found no duplicate
loan-month keys. The source file is not globally ordered by this key, so
uniqueness was tested explicitly; lack of global ordering is not itself a data-
quality defect. Observations without a complete future outcome window are
handled under the censoring rules specified in Chapter 3.

## 2.3. Data quality and reproducibility

Raw deliveries were checked for field count, the presence of loan identifiers
and reporting dates, and duplicate loan-month observations. The original 2008Q1
archive is retained without modification; its SHA-256 digest is
`6d9d3df9737fc321e70cc76bcbdf03a8bfe9ec190e472a1e1f2f9b9bd8460ae9`.
Recording the digest identifies the source version and supports reproducibility
of subsequent computations.

The official file layout was incorporated into a project dictionary. All 113
positions in the archive have official names, types, and descriptions. The
glossary also lists Origination VantageScore 4.0 at position 114, although it is
absent from the analysed 113-field delivery. This is treated as a format-version
difference rather than a missing observation.

## 2.4. Preparation principles

Blank and whitespace-only values are treated as missing. Reporting,
origination, first-payment, and legal-maturity fields are converted from
`MMYYYY` to calendar dates; numerical variables used in the analysis are cast
to numeric types. Special codes are retained until their meaning is assessed
under the outcome and feature rules, avoiding unsupported recoding.

The cleaned 113-field record and a 35-field monthly analytical base panel are
stored separately. Zero Balance Code and Zero Balance Effective Date are not
used as predictors because they may describe loan termination after the
prediction date. A field-level leakage register records the economic meaning,
temporal availability, and analytical treatment of each source field. It thus
separates variables used to construct outcomes from variables admissible for
prediction.

## 2.5. Scope of the prepared sample

The v01 development sample comprises seven Q1 cohorts and is not a complete
annual sample. Cohort identity is retained to preserve data provenance and
examine vintage differences.

Nine available Q3 cohorts (`2006Q3`–`2024Q3`, with gaps in years) were
processed for an origination-quarter robustness assessment. Together they
contain 281,706,562 rows, share the 113-field structure, pass the initial
quality checks, and follow the same preparation rules as Q1. Q3 data are not
added to the principal v01 training sample before an independent assessment of
model transportability. This preserves the distinction between model
development and independent validation. See the [Q3 audit](../17_q3_archive_audit_execution_report.md)
and [comparative analysis](../19_q1_q3_comparative_analysis_execution_report.md).

## 2.6. Source traceability

The official file layout and glossary are the primary basis for interpreting
fields, codes, and format-version differences [57]. Academic work on temporal
credit risk and explainability does not replace that specification; it informs
the experimental design, temporal validation, and model-auditability
requirements [6], [53], [55], [56].
