# Fannie Mae Primary Dataset

Active source: Fannie Mae Single-Family Loan Performance Primary Dataset,
acquisition cohort 2008Q1. The raw archive is immutable. It contains one
headerless CSV that combines static origination/acquisition characteristics and
dynamic monthly performance records.

Run stages 4–6 from this directory's parent with:

```bash
python3 src/fannie_mae/validate_fannie_zip.py \
  --source fannie_mae/data/raw/2008Q1/2008Q1.zip \
  --report fannie_mae/reports/2008Q1_raw_validation.json \
  --manifest fannie_mae/data/manifests/data_manifest.csv

python3 src/fannie_mae/build_fannie_monthly_panel.py \
  --source fannie_mae/data/raw/2008Q1/2008Q1.zip \
  --glossary fannie_mae/docs/sources/crt-file-layout-and-glossary.xlsx \
  --dictionary fannie_mae/data/dictionaries/fannie_2008q1_field_dictionary.csv \
  --cleaned fannie_mae/data/interim/2008Q1_cleaned.parquet \
  --panel fannie_mae/data/processed/2008Q1_monthly_panel_base.parquet \
  --event-metadata fannie_mae/data/interim/2008Q1_event_metadata.parquet \
  --report fannie_mae/reports/2008Q1_cleaning_and_panel.json
```

The panel is unlabelled and does not contain a model feature-selection decision.
The official glossary maps raw positions 1–113; glossary position 114 is not
present in this archive. Outcome construction and leakage controls are
subsequent stages.
