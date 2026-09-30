import { useEffect, useState } from 'react';
import AppSidebar from '../components/AppSidebar.jsx';
import Topbar from '../components/Topbar.jsx';
import EwsPages from '../pages/EwsPages.jsx';
import LoginGate from '../components/LoginGate.jsx';
import ResearchPages from '../pages/ResearchPages.jsx';
import { screenGroups } from './screenManifest.js';
import '../styles/app.css';

function App() {
  const [activeScreen, setActiveScreen] = useState('research-overview');
  const [language, setLanguage] = useState(() => sessionStorage.getItem('suptech_language') ?? 'ru');
  const [selectedAlertId, setSelectedAlertId] = useState(null);
  const [identity, setIdentity] = useState(() => {
    const token = sessionStorage.getItem('suptech_access_token');
    return token ? { username: sessionStorage.getItem('suptech_username'), role: sessionStorage.getItem('suptech_role') } : null;
  });
  useEffect(() => {
    document.documentElement.lang = language;
  }, [language]);
  const selectedScreen = screenGroups.flatMap((group) => group.screens)
    .find((screen) => screen.id === activeScreen);
  function logout() {
    ['suptech_access_token', 'suptech_role', 'suptech_username'].forEach((key) => sessionStorage.removeItem(key));
    setIdentity(null); setActiveScreen('research-overview'); setSelectedAlertId(null);
  }
  function changeLanguage(nextLanguage) {
    sessionStorage.setItem('suptech_language', nextLanguage);
    setLanguage(nextLanguage);
  }

  if (!identity) return <LoginGate language={language} onLanguageChange={changeLanguage} onAuthenticated={setIdentity} />;
  return (
    <div className="app-shell">
      <AppSidebar activeScreen={activeScreen} language={language} onNavigate={setActiveScreen} identity={identity} />
      <div className="app-shell__main">
        <Topbar language={language} onLanguageChange={changeLanguage} identity={identity} onLogout={logout} />
        <main className="app-content" id="main-content">
          {activeScreen.startsWith('research') ? <ResearchPages activeScreen={activeScreen} language={language} /> : ['ews-dashboard', 'ews-alert-queue', 'ews-alert-detail', 'ews-risk-monitoring', 'ews-governance', 'ews-administration'].includes(activeScreen) ? <EwsPages activeScreen={activeScreen} language={language} selectedAlertId={selectedAlertId} onSelectAlert={setSelectedAlertId} onNavigate={setActiveScreen} identity={identity} /> : (
            <section className="future-page" aria-labelledby="future-title">
              <p className="section-label">SupTech Early-Warning System</p>
              <h1 id="future-title">{selectedScreen?.title}</h1>
              <p>Этот экран будет реализован на следующих этапах. Научные результаты уже доступны в разделе Research Evidence.</p>
            </section>
          )}
        </main>
      </div>
    </div>
  );
}

export default App;
