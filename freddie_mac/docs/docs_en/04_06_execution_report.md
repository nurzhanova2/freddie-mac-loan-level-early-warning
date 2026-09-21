# Execution of stages 4–6: acquisition, cleaning and monthly panel

**Status as of 14 September 2026:** stage 4 awaits a matched analytical extract
from Clarity; stage 5 has been implemented and verified on the official example
files; stage 6 was intentionally not completed because the example files do not
form a matched dataset.

## 4. Data acquisition and initial validation

The official Freddie Mac page states that Standard Dataset, sample dataset and
full files are available through Clarity Data Intelligence after registration.
The available environment could not use an authenticated browser session, and
the workspace contains no matched vintage files downloaded from Clarity.

Rather than treating an example as analytical data, the published
`release-47-sample-files.zip` archive was downloaded. Its provenance, size,
SHA-256 checksum and row counts are recorded in
[`data_manifest.csv`](../../data/manifests/data_manifest.csv). Its use is
strictly limited to schema and pipeline validation.

## 5. Cleaning and standardisation

A reproducible script,
[`prepare_release_47.py`](../../src/freddie_mac/prepare_release_47.py), has been
implemented. It assigns official headers to pipe-delimited files, validates each
row width, converts blanks to `null`, parses `YYYYMM` dates, casts numeric
fields and replaces only documented `Not Available`/`Unknown` codes. The rules
are retained separately in
[`field_rules_release_47.yml`](../../config/field_rules_release_47.yml).

The example files were successfully cleaned into 1,000 origination records and
1,011 performance records. No invalid numeric or date values were detected in
the fields expected to have those formats; no null or duplicate
`loan_identifier` and `loan_identifier × period` keys were found. Detailed
outputs are available in:

- [origination cleaning QA](../../reports/release_47_example_origination_cleaning.json);
- [performance cleaning QA](../../reports/release_47_example_performance_cleaning.json).

These results validate the code against the example format; they do not make a
claim about the quality of the future analytical extract.

## 6. Construction of the monthly panel

The pipeline verifies referential integrity before merging the files. In the
example archive, all 12 performance-file loan identifiers are absent from the
origination file. The script stopped with `panel_status = invalid_input_pair`
and **did not create** a monthly-panel file. This prevents implicit rows with
missing origination characteristics from being represented as an analytical
dataset.

The blocking validation result is stored in
[`release_47_example_panel_build.json`](../../reports/release_47_example_panel_build.json).

## Condition for continuation

A matched Clarity pair for one vintage is required: `sample_orig_YYYY` with
`sample_perf_YYYY`, or `orig_YYYYQn` with `perf_YYYYQn`. Once placed in
`data/raw/<vintage>/`, the pipeline will carry out the same validation and
cleaning steps and produce `data/interim/<vintage>_monthly_panel_base.csv`.
The commands are provided in the project [README](../../README.md).
