import { useState } from 'react';
import DataTable from '../../../components/DataTable.jsx';
import { api } from '../../../data/apiClient.js';
import { ROLES, canAccessGovernance, canAdministerUsers } from '../../../app/accessPolicy.js';
import { ApiState, Title, useApi } from '../shared.jsx';

export function Governance({ copy, identity }) {
  const allowed = canAccessGovernance(identity?.role);
  const registry = useApi(() => allowed ? api.registry() : Promise.resolve(null), [allowed]);
  const audit = useApi(() => allowed ? api.audit() : Promise.resolve(null), [allowed]);
  if (!allowed) return <section className="ews-page"><Title label="SupTech Early-Warning System / E5" title={copy.governance} /><article className="panel access-notice"><p className="card-kicker">Controlled access</p><p>This view is available to model governance and data stewardship roles. Use the Alert Queue for controlled research viewing.</p></article></section>;
  return <section className="ews-page"><Title label="SupTech Early-Warning System / E5" title={copy.governance} /><div className="governance-grid"><article className="panel"><p className="card-kicker">Model registry</p><ApiState state={registry} copy={copy}>{registry.data && <dl className="detail-list"><dt>Model</dt><dd>{registry.data.model_version}</dd><dt>Data version</dt><dd>{registry.data.data_version}</dd><dt>Validation</dt><dd>{registry.data.validation}</dd><dt>Use status</dt><dd>{registry.data.use_status}</dd></dl>}</ApiState></article><article className="panel"><p className="card-kicker">Control boundaries</p><p className="audit-summary">The database stores review/audit events. Authentication and RBAC remain required before enabling approved research exports.</p></article></div><ApiState state={audit} copy={copy}>{audit.data && <article className="panel"><DataTable caption={copy.audit} columns={[{ key: 'occurred_at', label: 'Date' }, { key: 'alert_id', label: 'Alert' }, { key: 'actor', label: 'Actor' }, { key: 'event_type', label: 'Event' }]} rows={audit.data.items} /></article>}</ApiState></section>;
}

export function Administration({ copy, identity }) {
  const canAdmin = canAdministerUsers(identity?.role);
  const usersState = useApi(() => canAdmin ? api.users() : Promise.resolve(null), [canAdmin]);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [role, setRole] = useState('research_viewer');
  const [message, setMessage] = useState('');
  const [selectedUser, setSelectedUser] = useState(null);
  const [editedRole, setEditedRole] = useState('research_viewer');
  const [isActive, setIsActive] = useState(true);
  const [reason, setReason] = useState('');
  const [confirmed, setConfirmed] = useState(false);

  async function createUser(event) {
    event.preventDefault();
    try { await api.createUser({ username, password, role }); setMessage(`User ${username} created.`); setUsername(''); setPassword(''); window.location.reload(); }
    catch { setMessage('Could not create the user. Check role and username.'); }
  }
  function beginEdit(user) { setSelectedUser(user); setEditedRole(user.role); setIsActive(user.is_active); setReason(''); setConfirmed(false); setMessage(''); }
  async function saveUser(event) {
    event.preventDefault();
    if (!selectedUser) return;
    try { await api.updateUser(selectedUser.username, { role: editedRole, is_active: isActive, reason, confirmed }); setMessage(`Access for ${selectedUser.username} updated.`); window.location.reload(); }
    catch { setMessage('The access change was rejected. A reason, confirmation, a different actor, and at least one active platform administrator are required.'); }
  }

  if (!canAdmin) return <section className="ews-page"><Title label="SupTech Early-Warning System / E6" title="Administration" /><article className="panel access-notice"><p className="card-kicker">Controlled access</p><p>Administration requires model_governance or platform_admin.</p></article></section>;
  return <section className="ews-page"><Title label="SupTech Early-Warning System / E6" title="Administration" /><div className="admin-grid"><article className="panel"><p className="card-kicker">Create local user</p><form className="review-form review-form--plain" onSubmit={createUser}><label>Username<input value={username} onChange={(event) => setUsername(event.target.value)} required /></label><label>Temporary password<input type="password" value={password} onChange={(event) => setPassword(event.target.value)} minLength="8" required /></label><label>Role<select value={role} onChange={(event) => setRole(event.target.value)}>{ROLES.map((item) => <option key={item}>{item}</option>)}</select></label><button className="action-button">Create user</button></form></article><article className="panel"><p className="card-kicker">Workflow rules</p><ul className="governance-list"><li>Role changes require a reason and explicit confirmation.</li><li>Users cannot alter their own role or active status.</li><li>The last active platform administrator cannot be deactivated or demoted.</li><li>Every action is recorded in the persistent audit trail.</li></ul></article></div>{selectedUser && <article className="panel admin-edit"><p className="card-kicker">Edit access: {selectedUser.username}</p><form className="review-form review-form--plain" onSubmit={saveUser}><label>Role<select value={editedRole} onChange={(event) => setEditedRole(event.target.value)}>{ROLES.map((item) => <option key={item}>{item}</option>)}</select></label><label className="checkbox-label"><input type="checkbox" checked={isActive} onChange={(event) => setIsActive(event.target.checked)} /> Active account</label><label>Reason for change<textarea value={reason} onChange={(event) => setReason(event.target.value)} required /></label><label className="checkbox-label"><input type="checkbox" checked={confirmed} onChange={(event) => setConfirmed(event.target.checked)} required /> I confirm this access change.</label><div className="form-actions"><button className="action-button">Save access change</button><button className="secondary-button" type="button" onClick={() => setSelectedUser(null)}>Cancel</button></div></form></article>}{message && <p className="form-success">{message}</p>}<ApiState state={usersState} copy={copy}>{usersState.data && <article className="panel"><div className="admin-users"><DataTable caption="Local users" columns={[{ key: 'username', label: 'Username' }, { key: 'role', label: 'Role' }, { key: 'is_active', label: 'Status' }, { key: 'created_at', label: 'Created' }]} rows={usersState.data.items.map((user) => ({ ...user, is_active: user.is_active ? 'Active' : 'Deactivated', created_at: user.created_at.slice(0, 10) }))} />{usersState.data.items.map((user) => <button className="secondary-button admin-users__button" type="button" key={`${user.username}-change`} onClick={() => beginEdit(user)}>Edit {user.username}</button>)}</div></article>}</ApiState></section>;
}
