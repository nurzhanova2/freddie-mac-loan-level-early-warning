import { useState } from 'react';
import { api } from '../../../data/apiClient.js';
import { ApiState, driverLabel, Status, Tier, Title, useApi } from '../shared.jsx';

export function Queue({ copy, selectedAlertId, onSelectAlert, onNavigate }) {
  const [tier, setTier] = useState('All');
  const [reviewStatus, setReviewStatus] = useState('All');
  const [search, setSearch] = useState('');
  const state = useApi(() => api.alerts({ tier, review_status: reviewStatus }), [tier, reviewStatus]);
  const alerts = (state.data?.items ?? []).filter((item) => item.alert_id.toLowerCase().includes(search.toLowerCase()));
  const selected = alerts.find((item) => item.alert_id === selectedAlertId) ?? state.data?.items?.find((item) => item.alert_id === selectedAlertId);
  return <section className="ews-page"><Title label="SupTech Early-Warning System / E2" title={copy.queue} /><div className="filter-bar"><label>{copy.tier}<select value={tier} onChange={(event) => setTier(event.target.value)}><option>All</option><option>Red</option><option>Amber</option></select></label><label>{copy.status}<select value={reviewStatus} onChange={(event) => setReviewStatus(event.target.value)}><option>All</option><option>Pending</option><option>In review</option><option>Reviewed</option></select></label><label>{copy.search}<input value={search} onChange={(event) => setSearch(event.target.value)} /></label><span>{alerts.length}</span></div><ApiState state={state} copy={copy}><div className="queue-layout"><article className="queue-table"><div className="queue-table__scroll"><table><thead><tr><th>Alert ID</th><th>Loan ref.</th><th>Month</th><th>{copy.risk}</th><th>{copy.tier}</th><th>{copy.status}</th></tr></thead><tbody>{alerts.map((alert) => <tr key={alert.alert_id} className={alert.alert_id === selectedAlertId ? 'is-selected' : ''} onClick={() => onSelectAlert(alert.alert_id)}><td>{alert.alert_id}</td><td>{alert.loan_reference}</td><td>{alert.reporting_month}</td><td>{alert.risk_score.toFixed(3)}</td><td><Tier value={alert.tier} /></td><td><Status value={alert.review_status} /></td></tr>)}</tbody></table></div></article><aside className="triage-card"><p className="card-kicker">Selected alert</p>{selected ? <><strong>{selected.alert_id}</strong><p>{copy.driver}: {driverLabel(selected.top_shap_driver)}</p><button className="action-button" type="button" onClick={() => onNavigate('ews-alert-detail')}>{copy.open}</button></> : <p>Select an alert.</p>}</aside></div></ApiState></section>;
}

export function Detail({ copy, selectedAlertId }) {
  const alertId = selectedAlertId ?? 'ALT-2025-0001';
  const alertState = useApi(() => api.alert(alertId), [alertId]);
  const explanationState = useApi(() => api.explanation(alertId), [alertId]);
  const [decision, setDecision] = useState('Monitoring');
  const [comment, setComment] = useState('');
  const [helpfulness, setHelpfulness] = useState('');
  const [message, setMessage] = useState('');
  async function submit(event) {
    event.preventDefault();
    try { await api.createReview(alertId, { decision, comment, explanation_helpfulness: helpfulness ? Number(helpfulness) : null }); setMessage('Saved to persistent audit trail.'); }
    catch { setMessage(copy.error); }
  }
  return <section className="ews-page"><Title label="SupTech Early-Warning System / E3" title={copy.detail} /><ApiState state={alertState} copy={copy}>{alertState.data && <><div className="detail-header"><div><strong>{alertState.data.alert_id}</strong><span>{alertState.data.loan_reference} · {alertState.data.reporting_month} · {alertState.data.cohort}</span></div><Tier value={alertState.data.tier} /></div><div className="detail-grid"><article className="panel"><div className="score-block"><b>{alertState.data.risk_score.toFixed(3)}</b><span>{copy.risk}</span><em>{copy.threshold}: {alertState.data.trigger_threshold.toFixed(3)}</em></div><dl className="detail-list"><dt>{copy.target}</dt><dd>{alertState.data.target}</dd><dt>Model version</dt><dd>{alertState.data.model_version}</dd><dt>Data version</dt><dd>{alertState.data.data_version}</dd>{alertState.data.observed_outcome !== null && <><dt>Observed six-month outcome (audit only)</dt><dd>{alertState.data.observed_outcome ? 'Observed event' : 'No observed event'} · {alertState.data.outcome_observed_at}</dd></>}</dl></article><article className="panel"><p className="card-kicker">Local SHAP explanation</p><ApiState state={explanationState} copy={copy}>{explanationState.data && <><h2>{driverLabel(explanationState.data.top_driver)}</h2><div className="shap-explanation"><b>{explanationState.data.top_contribution.toFixed(3)}</b><i style={{ width: `${Math.min(Math.abs(explanationState.data.top_contribution) * 200, 100)}%` }} /></div></>}</ApiState></article></div><form className="review-form" onSubmit={submit}><p className="card-kicker">{copy.decision}</p><label>{copy.decision}<select value={decision} onChange={(event) => setDecision(event.target.value)}><option>Priority follow-up</option><option>Watchlist</option><option>Monitoring</option><option>No immediate action</option></select></label><label>{copy.comment}<textarea value={comment} onChange={(event) => setComment(event.target.value)} /></label><label>How useful was this explanation? (optional)<select value={helpfulness} onChange={(event) => setHelpfulness(event.target.value)}><option value="">Not rated</option><option value="1">1 — not useful</option><option value="2">2</option><option value="3">3</option><option value="4">4</option><option value="5">5 — very useful</option></select></label><button className="action-button">{copy.save}</button>{message && <p className="form-success">{message}</p>}</form></>}</ApiState></section>;
}
