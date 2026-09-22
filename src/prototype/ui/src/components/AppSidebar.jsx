import { screenGroups } from '../app/screenManifest.js';
import { canAccessScreen } from '../app/accessPolicy.js';

function AppSidebar({ activeScreen, language, onNavigate, identity }) {
  const russian = language === 'ru';
  return <aside className="sidebar">
    <a className="brand" href="#main-content"><span className="brand__mark">↗</span><span><strong>{russian ? 'Платформа SupTech-исследований' : 'SupTech Research Platform'}</strong><small>{russian ? 'СРП ухудшения состояния заёмщика' : 'Borrower Deterioration EWS'}</small></span></a>
    <nav className="sidebar__nav" aria-label="Platform navigation">
      {screenGroups.map((group) => <section className="nav-group" key={group.id}>
        <h2>{russian ? group.ruLabel : group.label}</h2>
        {group.screens.filter((screen) => canAccessScreen(identity.role, screen.id)).map((screen) => <button className={`nav-item ${screen.id === activeScreen ? 'nav-item--active' : ''}`} key={screen.id} onClick={() => onNavigate(screen.id)} type="button" aria-current={screen.id === activeScreen ? 'page' : undefined}><span>{screen.id.startsWith('research') ? 'R' : 'E'}</span>{russian ? screen.ruTitle : screen.title}</button>)}
      </section>)}
    </nav>
    <p className="sidebar__footer">{russian ? 'Исследовательский прототип для диссертации. Не является промышленной надзорной системой.' : 'Research prototype for academic dissertation use. Not a production supervisory system.'}</p>
  </aside>;
}

export default AppSidebar;
