"""Black-box integration tests for a running local SupTech API.

Run after `docker compose up --build`:
    python3 -m unittest tests.api.test_live_api
"""
import json
import os
import time
import unittest
from urllib.error import HTTPError
from urllib.request import Request, urlopen


BASE_URL = os.environ.get('SUPTECH_API_BASE_URL', 'http://localhost:8000/api/v1')


def request(path, method='GET', payload=None, token=None):
    body = json.dumps(payload).encode() if payload is not None else None
    headers = {'Content-Type': 'application/json'} if body else {}
    if token: headers['Authorization'] = f'Bearer {token}'
    with urlopen(Request(f'{BASE_URL}{path}', data=body, headers=headers, method=method), timeout=10) as response:
        return json.load(response)


class SuptechApiIntegrationTests(unittest.TestCase):
    def login(self, username):
        return request('/auth/login', method='POST', payload={'username': username, 'password': 'demo-password-change-me'})['data']['access_token']

    def test_contract_never_allows_raw_data(self):
        response = request('/contract', token=self.login('demo_research_viewer'))
        self.assertIn('synthetic_demo_only', response['data_classification'])
        self.assertIn('raw_files', response['data']['forbidden_classes'])
        self.assertNotIn('loan_id', response['data']['allowed_browser_fields'])

    def test_alert_query_and_persistent_review_audit(self):
        analyst_token = self.login('demo_risk_analyst')
        alerts = request('/alerts?tier=Red&limit=1', token=analyst_token)['data']['items']
        self.assertEqual(len(alerts), 1)
        alert_id = alerts[0]['alert_id']
        review = request(f'/alerts/{alert_id}/reviews', method='POST', payload={'decision': 'Monitoring', 'comment': 'Automated integration-test review.'}, token=analyst_token)
        self.assertEqual(review['data']['review_status'], 'Reviewed')
        events = request('/audit-events', token=self.login('demo_model_governance'))['data']['items']
        self.assertTrue(any(event['alert_id'] == alert_id and event['event_type'] == 'expert_review_recorded' for event in events))

    def test_viewer_cannot_create_expert_review(self):
        viewer_token = self.login('demo_research_viewer')
        with self.assertRaises(HTTPError) as result:
            request('/alerts/ALT-2025-0001/reviews', method='POST', payload={'decision': 'Monitoring'}, token=viewer_token)
        self.assertEqual(result.exception.code, 403)

    def test_admin_user_lifecycle_is_audited(self):
        admin_token = self.login('demo_platform_admin')
        username = f'admin_test_{int(time.time() * 1000)}'
        created = request('/admin/users', method='POST', payload={'username': username, 'password': 'test-password-123', 'role': 'research_viewer'}, token=admin_token)['data']
        self.assertTrue(created['is_active'])
        updated = request(f'/admin/users/{username}', method='PATCH', payload={'role': 'risk_analyst', 'is_active': False, 'reason': 'Integration test lifecycle.', 'confirmed': True}, token=admin_token)['data']
        self.assertEqual(updated['role'], 'risk_analyst')
        self.assertFalse(updated['is_active'])
        with self.assertRaises(HTTPError) as inactive_login:
            request('/auth/login', method='POST', payload={'username': username, 'password': 'test-password-123'})
        self.assertEqual(inactive_login.exception.code, 401)
        governance_token = self.login('demo_model_governance')
        events = request('/audit-events', token=governance_token)['data']['items']
        self.assertTrue(any(event['event_type'] == 'user_access_updated' and event['payload']['username'] == username for event in events))

    def test_admin_workflow_protects_self_and_last_admin(self):
        admin_token = self.login('demo_platform_admin')
        with self.assertRaises(HTTPError) as self_change:
            request('/admin/users/demo_platform_admin', method='PATCH', payload={'role': 'research_viewer', 'reason': 'Forbidden self change.', 'confirmed': True}, token=admin_token)
        self.assertEqual(self_change.exception.code, 400)
        governance_token = self.login('demo_model_governance')
        with self.assertRaises(HTTPError) as last_admin:
            request('/admin/users/demo_platform_admin', method='PATCH', payload={'role': 'research_viewer', 'reason': 'Attempt to remove final admin.', 'confirmed': True}, token=governance_token)
        self.assertEqual(last_admin.exception.code, 400)
