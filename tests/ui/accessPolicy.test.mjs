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
