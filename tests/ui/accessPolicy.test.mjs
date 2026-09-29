import assert from 'node:assert/strict';
import test from 'node:test';

import {
  ROLES,
  canAccessGovernance,
  canAccessScreen,
  canAdministerUsers,
} from '../../src/prototype/ui/src/app/accessPolicy.js';

test('every declared role can access research screens', () => {
  for (const role of ROLES) assert.equal(canAccessScreen(role, 'research-overview'), true);
});

test('alert viewers cannot access governance or administration', () => {
  for (const role of ['research_viewer', 'risk_analyst']) {
    assert.equal(canAccessGovernance(role), false);
    assert.equal(canAdministerUsers(role), false);
    assert.equal(canAccessScreen(role, 'ews-governance'), false);
    assert.equal(canAccessScreen(role, 'ews-administration'), false);
  }
});

test('governance and administration permissions follow the role policy', () => {
  assert.equal(canAccessGovernance('model_governance'), true);
  assert.equal(canAccessGovernance('data_steward'), true);
  assert.equal(canAdministerUsers('model_governance'), true);
  assert.equal(canAdministerUsers('platform_admin'), true);
  assert.equal(canAccessScreen('platform_admin', 'ews-alert-queue'), false);
});

test('all five roles follow the declared controlled-screen matrix', () => {
  const expected = {
    research_viewer: { alerts: true, governance: false, administration: false },
    risk_analyst: { alerts: true, governance: false, administration: false },
    model_governance: { alerts: true, governance: true, administration: true },
    data_steward: { alerts: true, governance: true, administration: false },
    platform_admin: { alerts: false, governance: false, administration: true },
  };
  for (const [role, access] of Object.entries(expected)) {
    assert.equal(canAccessScreen(role, 'research-overview'), true, `${role}: research overview`);
    assert.equal(canAccessScreen(role, 'ews-alert-queue'), access.alerts, `${role}: alert queue`);
    assert.equal(canAccessScreen(role, 'ews-governance'), access.governance, `${role}: model governance`);
    assert.equal(canAccessScreen(role, 'ews-administration'), access.administration, `${role}: administration`);
  }
});
