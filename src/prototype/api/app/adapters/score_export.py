"""Load a pre-approved alert score export without exposing raw source data."""
import csv
import os
from pathlib import Path

from ..seed import ALERTS as SYNTHETIC_ALERTS

ALLOWED_FIELDS = {
    'alert_id', 'loan_reference', 'cohort', 'reporting_month', 'target',
    'risk_score', 'trigger_threshold', 'tier', 'top_shap_driver',
    'top_shap_contribution', 'review_status', 'expert_decision',
}
FORBIDDEN_MARKERS = {'loan_id', 'raw_path', 'feature_vector', 'training_sample', 'servicing_history'}


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
        if not ALLOWED_FIELDS.issuperset(columns) or columns.intersection(FORBIDDEN_MARKERS):
            raise ValueError('Approved export contains a forbidden or unsupported field')
        required = ALLOWED_FIELDS - {'expert_decision'}
        if not required.issubset(columns):
            raise ValueError('Approved export is missing required alert fields')
        rows = []
        for row in reader:
            rows.append({
                **row,
                'risk_score': float(row['risk_score']),
                'trigger_threshold': float(row['trigger_threshold']),
                'top_shap_contribution': float(row['top_shap_contribution']),
            })
    return rows, 'approved_research_export'
