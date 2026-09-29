import { useEffect, useState } from 'react';

export const labels = {
  ru: { dashboard: 'Панель раннего предупреждения', queue: 'Очередь сигналов', detail: 'Карточка сигнала', governance: 'Управление моделью', tier: 'Tier', status: 'Статус', risk: 'Risk score', threshold: 'Порог', driver: 'Ведущий фактор SHAP', target: 'Целевой исход', save: 'Зафиксировать в журнале', decision: 'Решение эксперта', comment: 'Комментарий эксперта', loading: 'Загрузка данных API…', error: 'Не удалось загрузить данные API. Убедитесь, что suptech-api запущен.', search: 'Поиск Alert ID', open: 'Открыть карточку сигнала', audit: 'Журнал аудита' },
  en: { dashboard: 'Early-Warning Dashboard', queue: 'Alert Queue', detail: 'Alert Detail', governance: 'Model Governance', tier: 'Tier', status: 'Status', risk: 'Risk score', threshold: 'Threshold', driver: 'Top SHAP driver', target: 'Target', save: 'Record in audit trail', decision: 'Expert decision', comment: 'Expert comment', loading: 'Loading API data…', error: 'Could not load API data. Confirm suptech-api is running.', search: 'Search Alert ID', open: 'Open alert detail', audit: 'Audit trail' },
};

const driverNames = {
  current_delinquency_status: 'Current delinquency status',
  original_interest_rate: 'Original interest rate',
  borrower_credit_score_at_origination: 'FICO at origination',
  debt_to_income_dti: 'Debt-to-income ratio',
  current_interest_rate: 'Current interest rate',
  loan_age: 'Loan age',
  original_combined_loan_to_value_ratio_cltv: 'Original CLTV',
  property_state: 'Property state',
};

export const driverLabel = (value) => driverNames[value] ?? value;
export const Tier = ({ value }) => <span className={`tier tier--${value.toLowerCase()}`} aria-label={`Risk tier: ${value}`}>{value}</span>;
export const Status = ({ value }) => <span className={`status status--${value.toLowerCase().replace(' ', '-')}`} aria-label={`Review status: ${value}`}>{value}</span>;
export const Title = ({ label, title }) => <header className="page-title"><p className="section-label">{label}</p><h1>{title}</h1></header>;

export function useApi(load, dependencies = []) {
  const [state, setState] = useState({ loading: true, error: null, data: null });
  useEffect(() => {
    let active = true;
    setState({ loading: true, error: null, data: null });
    load()
      .then((data) => active && setState({ loading: false, error: null, data }))
      .catch((error) => active && setState({ loading: false, error: error.message, data: null }));
    return () => { active = false; };
  }, dependencies);
  return state;
}

export function ApiState({ state, copy, children }) {
  if (state.loading) return <p className="api-state api-state--loading" role="status">{copy.loading}</p>;
  if (state.error) {
    const accessError = state.error === 'API 401' || state.error === 'API 403';
    return <p className="api-state api-state--error" role="alert">{accessError ? 'This role does not have access to this controlled view.' : copy.error}</p>;
  }
  return children;
}
