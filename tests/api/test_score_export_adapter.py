import csv
import os
import tempfile
import unittest
from pathlib import Path

from src.prototype.api.app.adapters.score_export import load_approved_alert_export


class ApprovedScoreExportAdapterTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tempdir.name)
        self.old_root = os.environ.get('SUPTECH_APPROVED_EXPORTS_ROOT')
        self.old_export = os.environ.get('SUPTECH_APPROVED_ALERT_EXPORT')
        os.environ['SUPTECH_APPROVED_EXPORTS_ROOT'] = str(self.root)

    def tearDown(self):
        if self.old_root is None: os.environ.pop('SUPTECH_APPROVED_EXPORTS_ROOT', None)
        else: os.environ['SUPTECH_APPROVED_EXPORTS_ROOT'] = self.old_root
        if self.old_export is None: os.environ.pop('SUPTECH_APPROVED_ALERT_EXPORT', None)
        else: os.environ['SUPTECH_APPROVED_ALERT_EXPORT'] = self.old_export
        self.tempdir.cleanup()

    def test_loads_only_minimal_approved_dto(self):
        path = self.root / 'approved_alerts.csv'
        fields = ['alert_id', 'loan_reference', 'cohort', 'reporting_month', 'target', 'risk_score', 'trigger_threshold', 'tier', 'top_shap_driver', 'top_shap_contribution', 'review_status']
        with path.open('w', newline='', encoding='utf-8') as handle:
            writer = csv.DictWriter(handle, fieldnames=fields)
            writer.writeheader()
            writer.writerow({'alert_id': 'ALT-1', 'loan_reference': 'REF-1', 'cohort': '2024Q1', 'reporting_month': '2025-01', 'target': 'early_deterioration_6m', 'risk_score': '.2', 'trigger_threshold': '.1', 'tier': 'Amber', 'top_shap_driver': 'loan_age', 'top_shap_contribution': '.05', 'review_status': 'Pending'})
        os.environ['SUPTECH_APPROVED_ALERT_EXPORT'] = str(path)
        rows, classification = load_approved_alert_export()
        self.assertEqual(classification, 'approved_research_export')
        self.assertEqual(rows[0]['risk_score'], .2)

    def test_rejects_raw_field(self):
        path = self.root / 'unsafe.csv'
        path.write_text('alert_id,loan_id\nALT-1,stable-source-id\n', encoding='utf-8')
        os.environ['SUPTECH_APPROVED_ALERT_EXPORT'] = str(path)
        with self.assertRaises(ValueError):
            load_approved_alert_export()
