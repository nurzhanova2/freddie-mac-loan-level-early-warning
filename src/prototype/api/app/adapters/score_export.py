"""Load a pre-approved alert score export without exposing raw source data."""
import csv
import os
from pathlib import Path

from ..seed import ALERTS as SYNTHETIC_ALERTS
from ..alert_contract import is_valid_export_columns


def load_approved_alert_export() -> tuple[list[dict], str]:
    """Return synthetic seed by default; load only a configured approved CSV otherwise."""
    export_path = os.environ.get('SUPTECH_APPROVED_ALERT_EXPORT')
    if not export_path:
        return SYNTHETIC_ALERTS, 'synthetic_demo_only'
    root = Path(os.environ.get('SUPTECH_APPROVED_EXPORTS_ROOT', '/app/approved_exports')).resolve()
    candidate = Path(export_path).resolve()
    if root not in candidate.parents or candidate.suffix.lower() != '.csv':
        raise ValueError('Approved export must be a CSV inside SUPTECH_APPROVED_EXPORTS_ROOT')
    with candidate.open(newline='', encoding='utf-8') as handle:
        reader = csv.DictReader(handle)
        columns = set(reader.fieldnames or [])
        if not is_valid_export_columns(columns):
            raise ValueError('Approved export contains a forbidden or unsupported field')
        rows = []
        for row in reader:
            rows.append({
                **row,
                'risk_score': float(row['risk_score']),
                'trigger_threshold': float(row['trigger_threshold']),
                'top_shap_contribution': float(row['top_shap_contribution']),
            })
    return rows, 'approved_research_export'
