import { demoAlerts, initialAuditEntries } from './demoAlerts.js';

// GitHub Pages can serve only static assets. This adapter deliberately exposes
// the same de-identified synthetic alert contract as the local demo, without
// making a network request or shipping source Fannie Mae records to a browser.
const DEMO_PASSWORD = 'demo-password-change-me';
const USERS_KEY = 'suptech_static_demo_users_v01';
const AUDIT_KEY = 'suptech_static_demo_audit_v01';
const roles = new Map([
  ['demo_research_viewer', 'research_viewer'],
  ['demo_risk_analyst', 'risk_analyst'],
  ['demo_model_governance', 'model_governance'],
  ['demo_data_steward', 'data_steward'],
  ['demo_platform_admin', 'platform_admin'],
]);

const clone = (value) => JSON.parse(JSON.stringify(value));
const now = () => new Date().toISOString();
const currentUser = () => sessionStorage.getItem('suptech_username') ?? 'static_demo';
const currentRole = () => sessionStorage.getItem('suptech_role');

function requireRole(...allowed) {
  if (!allowed.includes(currentRole())) throw new Error('API 403');
}

function storedUsers() {
  const saved = sessionStorage.getItem(USERS_KEY);
  if (saved) return JSON.parse(saved);
  return [...roles.entries()].map(([username, role]) => ({ username, role, is_active: true, created_at: '2026-09-30T00:00:00.000Z' }));
}

function saveUsers(users) {
  sessionStorage.setItem(USERS_KEY, JSON.stringify(users));
}

function storedAudit() {
  const saved = sessionStorage.getItem(AUDIT_KEY);
  if (saved) return JSON.parse(saved);
  return initialAuditEntries.map((entry, index) => ({
    event_id: `static-seed-${index + 1}`,
    alert_id: entry.alertId,
    actor: entry.actor,
    event_type: 'expert_review_recorded',
    occurred_at: `${entry.recordedAt}T12:00:00.000Z`,
  }));
}

function saveAudit(events) {
  sessionStorage.setItem(AUDIT_KEY, JSON.stringify(events));
}

function alertDto(alert) {
  return {
    alert_id: alert.alertId,
    loan_reference: alert.loanId,
    cohort: alert.cohort,
    reporting_month: alert.reportingMonth,
    target: alert.target,
    risk_score: alert.riskScore,
    trigger_threshold: alert.threshold,
    tier: alert.tier,
    top_shap_driver: alert.topDriver,
    top_shap_contribution: alert.contribution,
    review_status: alert.reviewStatus,
    expert_decision: alert.decision || null,
    observed_outcome: alert.outcome === 'Unobserved' ? null : Number(alert.outcome !== 'No event'),
    outcome_observed_at: alert.outcome === 'Unobserved' ? null : `${alert.reportingMonth}-30`,
    model_version: alert.modelVersion,
    data_version: alert.dataVersion,
  };
}

function addAudit(event) {
  const events = storedAudit();
  events.unshift({ event_id: `static-${Date.now()}`, occurred_at: now(), ...event });
  saveAudit(events);
}

export const staticDemoApi = {
  async login(username, password) {
    const user = storedUsers().find((item) => item.username === username && item.is_active);
    if (!user || password !== DEMO_PASSWORD) throw new Error('API 401');
    return { access_token: `static-demo-${username}`, token_type: 'bearer', role: user.role, username: user.username };
  },
  async metrics() {
    requireRole('research_viewer', 'risk_analyst', 'model_governance', 'data_steward');
    const alerts = demoAlerts.map(alertDto);
    return {
      alert_count: alerts.length,
      red_alert_count: alerts.filter((alert) => alert.tier === 'Red').length,
      amber_alert_count: alerts.filter((alert) => alert.tier === 'Amber').length,
      requires_review_count: alerts.filter((alert) => alert.review_status !== 'Reviewed').length,
    };
  },
  async evaluation() {
    return { status: 'static_interface_demo_not_a_user_study', tiers: [], review_actions: storedAudit().length, explanation_ratings_count: 0, mean_explanation_helpfulness: null };
  },
  async alerts(params = {}) {
    requireRole('research_viewer', 'risk_analyst', 'model_governance', 'data_steward');
    const items = demoAlerts.map(alertDto).filter((alert) => (
      (!params.tier || params.tier === 'All' || alert.tier === params.tier)
      && (!params.review_status || params.review_status === 'All' || alert.review_status === params.review_status)
    ));
    return { count: items.length, items: clone(items) };
  },
  async alert(alertId) {
    requireRole('research_viewer', 'risk_analyst', 'model_governance', 'data_steward');
    const item = demoAlerts.map(alertDto).find((alert) => alert.alert_id === alertId);
    if (!item) throw new Error('API 404');
    return clone(item);
  },
  async explanation(alertId) {
    const alert = await this.alert(alertId);
    return { alert_id: alert.alert_id, method: 'SHAP', top_driver: alert.top_shap_driver, top_contribution: alert.top_shap_contribution, model_version: alert.model_version };
  },
  async registry() {
    requireRole('model_governance', 'data_steward');
    return {
      model_version: 'calibrated_xgboost_v01',
      data_version: 'fannie_panel_v01',
      targets: ['formal_adverse_6m', 'early_deterioration_6m'],
      validation: 'Temporal OOT validation; Q1 natural-size sensitivity and v02 Q1+Q3 tree-model OOT governance evaluation completed with no registry change; research prototype only.',
      use_status: 'research_prototype_only',
      registry_decision: { status: 'No registry change', message: 'v02 Q1+Q3 tree-model evaluation completed; no registry change.', active_model: 'calibrated_xgboost_v01' },
    };
  },
  async audit() {
    requireRole('model_governance', 'data_steward');
    return { count: storedAudit().length, items: clone(storedAudit()) };
  },
  async createReview(alertId, payload) {
    requireRole('risk_analyst', 'model_governance');
    addAudit({ alert_id: alertId, actor: currentUser(), event_type: 'expert_review_recorded' });
    return { review_id: `static-review-${Date.now()}`, alert_id: alertId, ...payload, reviewed_at: now(), review_status: 'Reviewed' };
  },
  async users() {
    requireRole('model_governance', 'platform_admin');
    return { items: clone(storedUsers()) };
  },
  async createUser(payload) {
    requireRole('model_governance', 'platform_admin');
    const users = storedUsers();
    if (users.some((user) => user.username === payload.username)) throw new Error('API 409');
    const user = { username: payload.username, role: payload.role, is_active: true, created_at: now() };
    users.push(user);
    saveUsers(users);
    addAudit({ alert_id: null, actor: currentUser(), event_type: 'user_created' });
    return clone(user);
  },
  async updateUser(username, payload) {
    requireRole('model_governance', 'platform_admin');
    if (!payload.confirmed || currentUser() === username) throw new Error('API 400');
    const users = storedUsers();
    const user = users.find((item) => item.username === username);
    if (!user) throw new Error('API 404');
    const activeAdmins = users.filter((item) => item.role === 'platform_admin' && item.is_active);
    const removesLastAdmin = user.role === 'platform_admin' && user.is_active && (payload.role !== 'platform_admin' || payload.is_active === false);
    if (removesLastAdmin && activeAdmins.length <= 1) throw new Error('API 400');
    if (payload.role) user.role = payload.role;
    if (typeof payload.is_active === 'boolean') user.is_active = payload.is_active;
    saveUsers(users);
    addAudit({ alert_id: null, actor: currentUser(), event_type: 'user_access_updated' });
    return clone(user);
  },
};
