# Freddie Mac loan-level early-warning dataset

## Current status

The project contains a validated Release 47 schema, a reproducible manifest,
and a cleaning/panel-building pipeline. The public Release 47 example archive
is intentionally **not** used as analytical data: its origination and
performance files have no overlapping loan identifiers.

To run stages 4–6, download a matched pair from Freddie Mac Clarity and place
the files under `data/raw/<vintage>/`.

```bash
python3 src/freddie_mac/validate_raw_files.py \
  --origination data/raw/<vintage>/sample_orig_YYYY.txt \
  --performance data/raw/<vintage>/sample_perf_YYYY.txt \
  --output reports/<vintage>_raw_validation.json

python3 src/freddie_mac/prepare_release_47.py clean-origination \
  --source data/raw/<vintage>/sample_orig_YYYY.txt \
  --output data/interim/<vintage>_origination_clean.csv \
  --audit reports/<vintage>_origination_cleaning.json

python3 src/freddie_mac/prepare_release_47.py clean-performance \
  --source data/raw/<vintage>/sample_perf_YYYY.txt \
  --output data/interim/<vintage>_performance_clean.csv \
  --audit reports/<vintage>_performance_cleaning.json

python3 src/freddie_mac/prepare_release_47.py build-panel \
  --origination data/interim/<vintage>_origination_clean.csv \
  --performance data/interim/<vintage>_performance_clean.csv \
  --output data/interim/<vintage>_monthly_panel_base.csv \
  --audit reports/<vintage>_panel_build.json
```

The scripts stop rather than create a panel when identifiers are not a fully
matched pair. They do not create labels or select model features.
