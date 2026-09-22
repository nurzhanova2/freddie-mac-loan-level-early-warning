export const ROLES = Object.freeze([
  'research_viewer',
  'risk_analyst',
  'model_governance',
  'data_steward',
  'platform_admin',
]);

const ALERT_VIEWERS = Object.freeze([
  'research_viewer',
  'risk_analyst',
  'model_governance',
  'data_steward',
]);
const GOVERNANCE_USERS = Object.freeze(['model_governance', 'data_steward']);
const ADMINISTRATORS = Object.freeze(['model_governance', 'platform_admin']);

export const screenRoles = Object.freeze({
  'ews-dashboard': ALERT_VIEWERS,
  'ews-alert-queue': ALERT_VIEWERS,
  'ews-alert-detail': ALERT_VIEWERS,
  'ews-risk-monitoring': ALERT_VIEWERS,
  'ews-governance': GOVERNANCE_USERS,
  'ews-administration': ADMINISTRATORS,
});

export function canAccessScreen(role, screenId) {
  const allowedRoles = screenRoles[screenId];
  return !allowedRoles || allowedRoles.includes(role);
}

export function canAccessGovernance(role) {
  return GOVERNANCE_USERS.includes(role);
}

export function canAdministerUsers(role) {
  return ADMINISTRATORS.includes(role);
}
