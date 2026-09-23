# Chapter 2. Construction and preparation of the Fannie Mae dataset

## 2.1. Data source and empirical scope

The empirical basis of the study is the Fannie Mae Single-Family Loan
Performance Primary Dataset, distributed through the Data Dynamics platform
[57]. It contains origination characteristics and subsequent monthly
mortgage-performance records. The present study covers the `2006Q1`, `2008Q1`, `2012Q1`, `2016Q1`,
`2020Q1`, `2022Q1`, and `2024Q1` acquisition cohorts. The analysis is confined
to the Primary Dataset; HARP, multifamily, and Freddie Mac data are not pooled
because they require separate definitions and processing rules.

The source population consists of conventional, fully amortising,
full-documentation, fixed-rate mortgages with an original term of no more than
30 years. Consequently, the findings concern this defined population and should
not be generalised to all U.S. mortgages. The seven panels contain 185,931,842
loan-month observations and 3,343,420 loans. Their coverage and origination
characteristics are reported in **Tables 2.1–2.2** — [“Cohort coverage”](../../../reports/eda_v01/01_cohort_overview.csv)
and [“Origination characteristics”](../../../reports/eda_v01/03_origination_characteristics.csv) —
and in **Figure 2.1** — [“Characteristics by cohort”](../../../reports/figures/eda_v01/03_origination_characteristics_trend.png).

## 2.2. Observational structure

The unit of analysis is a loan-month pair, consisting of a loan identifier and
a monthly reporting period. The resulting longitudinal panel is unbalanced:
loans may contribute different numbers of monthly observations. This structure
is appropriate for the research question because risk is assessed repeatedly as
new performance information becomes available.

The initial 2008Q1 delivery contains 22,415,219 records and 380,832 loans from
January 2008 through March 2026. An external-sort audit found no duplicate
loan-month keys. The source file is not globally ordered by this key, a property
that necessitates an explicit uniqueness check but does not itself imply a data
quality defect. Observations without a complete future outcome window are
addressed through the censoring rules in Chapter 3.

## 2.3. Data quality and reproducibility

Raw deliveries were checked for field count, non-empty loan and reporting-month
keys, and duplicate loan-month observations. The original 2008Q1 archive is
retained without modification; its SHA-256 digest is
`6d9d3df9737fc321e70cc76bcbdf03a8bfe9ec190e472a1e1f2f9b9bd8460ae9`.
Recording the source digest makes the empirical version identifiable and allows
subsequent computations to be reproduced.

The official file layout was incorporated into a project dictionary. All 113
positions in the archive have official names, types, and descriptions. The
source glossary also lists Origination VantageScore 4.0 at position 114, which
is absent from the analysed 113-field delivery; this is treated as a
format-version distinction rather than as a missing observation.

## 2.4. Preparation principles

Blank and whitespace-only values are represented as missing. Reporting,
origination, first-payment, and legal-maturity fields are converted from their
source `MMYYYY` representation to calendar dates; variables used in the
analysis are converted to appropriate numeric types. Special codes are retained
until their meaning is evaluated under the outcome and feature rules, avoiding
unsupported recoding.

The cleaned 113-field record and a 35-field monthly analytical base panel are
retained separately. Zero Balance Code and Zero Balance Effective Date are
excluded from predictors because they may characterise loan termination after
the prediction date. A field-level leakage register records the economic
meaning, temporal availability, and analytical treatment of every source field.
This separation preserves the distinction between variables used to construct
outcomes and variables admissible for prediction.

## 2.5. Scope of the prepared sample

The v01 development sample consists of seven Q1 cohorts and does not constitute
a complete annual sample. Cohort identity is retained in downstream analysis to
preserve provenance and to permit examination of vintage heterogeneity.

For an origination-quarter robustness assessment, nine available Q3 cohorts
(`2006Q3`–`2024Q3`, with gaps in years) have been processed. Together they
contain 281,706,562 rows, use the same 113-field structure, and satisfy the
initial quality checks. The Q3 workstream is not added to the principal v01
development sample before an independent transportability assessment. This
preserves the distinction between model development and validation. See the
[Q3 audit](../17_q3_archive_audit_execution_report.md) and the [comparative analysis](../19_q1_q3_comparative_analysis_execution_report.md).

## 2.6. Source traceability

The official file layout and glossary are the primary source for interpreting
fields, codes, and format-version differences [57]. Academic sources on the
temporal structure of credit risk and explainability do not replace that
specification; they inform the experimental design, temporal validation, and
model-auditability requirements [6], [53], [55], [56].
