import { Detail, Queue } from '../features/ews/alerts/AlertPages.jsx';
import { Governance, Administration } from '../features/ews/governance/GovernancePages.jsx';
import { Dashboard, RiskMonitoring } from '../features/ews/monitoring/MonitoringPages.jsx';
import { labels } from '../features/ews/shared.jsx';

function EwsPages({ activeScreen, language, selectedAlertId, onSelectAlert, onNavigate, identity }) {
  const copy = labels[language];
  if (activeScreen === 'ews-dashboard') return <Dashboard copy={copy} />;
  if (activeScreen === 'ews-alert-detail') return <Detail copy={copy} selectedAlertId={selectedAlertId} />;
  if (activeScreen === 'ews-risk-monitoring') return <RiskMonitoring copy={copy} language={language} />;
  if (activeScreen === 'ews-governance') return <Governance copy={copy} identity={identity} />;
  if (activeScreen === 'ews-administration') return <Administration copy={copy} identity={identity} />;
  return <Queue copy={copy} selectedAlertId={selectedAlertId} onSelectAlert={onSelectAlert} onNavigate={onNavigate} />;
}

export default EwsPages;
