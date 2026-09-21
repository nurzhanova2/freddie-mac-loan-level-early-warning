const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000/api/v1';

async function request(path, options) {
  const token = sessionStorage.getItem('suptech_access_token');
  const response = await fetch(`${BASE_URL}${path}`, { headers: { 'Content-Type': 'application/json', ...(token ? { Authorization: `Bearer ${token}` } : {}) }, ...options });
  if (!response.ok) throw new Error(`API ${response.status}`);
  const payload = await response.json();
  return payload.data;
}

export const api = {
  login: (username, password) => request('/auth/login', { method: 'POST', body: JSON.stringify({ username, password }) }),
  metrics: () => request('/metrics/overview'),
  alerts: (params = {}) => request(`/alerts?${new URLSearchParams(Object.entries(params).filter(([, value]) => value && value !== 'All'))}`),
  alert: (alertId) => request(`/alerts/${alertId}`),
  explanation: (alertId) => request(`/alerts/${alertId}/explanation`),
  registry: () => request('/model-registry'),
  audit: () => request('/audit-events'),
  createReview: (alertId, payload) => request(`/alerts/${alertId}/reviews`, { method: 'POST', body: JSON.stringify(payload) }),
  users: () => request('/admin/users'),
  createUser: (payload) => request('/admin/users', { method: 'POST', body: JSON.stringify(payload) }),
  updateUser: (username, payload) => request(`/admin/users/${username}`, { method: 'PATCH', body: JSON.stringify(payload) }),
};
