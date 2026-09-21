import { useState } from 'react';
import { api } from '../data/apiClient.js';

function LoginGate({ onAuthenticated }) {
  const [username, setUsername] = useState('demo_risk_analyst');
  const [password, setPassword] = useState('demo-password-change-me');
  const [error, setError] = useState('');
  const [language, setLanguage] = useState('ru');
  const russian = language === 'ru';
  async function submit(event) {
    event.preventDefault();
    setError('');
    try {
      const result = await api.login(username, password);
      sessionStorage.setItem('suptech_access_token', result.access_token);
      sessionStorage.setItem('suptech_role', result.role);
      sessionStorage.setItem('suptech_username', result.username);
      onAuthenticated({ username: result.username, role: result.role });
    } catch {
      setError(russian ? 'Не удалось выполнить вход. Проверьте логин и пароль локальной учётной записи.' : 'Login failed. Check the local development credentials.');
    }
  }
  return <main className="login-gate"><section><div className="login-gate__heading"><div><p className="section-label">{russian ? 'Локальная авторизация' : 'Local development access'}</p><h1>{russian ? 'Платформа SupTech-исследований' : 'SupTech Research Platform'}</h1></div><div className="language-switch" aria-label="Interface language"><button className={russian ? 'is-active' : ''} type="button" onClick={() => setLanguage('ru')}>RU</button><button className={!russian ? 'is-active' : ''} type="button" onClick={() => setLanguage('en')}>EN</button></div></div><p>{russian ? 'Войдите для доступа к контролируемому исследовательскому прототипу.' : 'Sign in to access the controlled research prototype.'}</p><form onSubmit={submit}><label>{russian ? 'Логин' : 'Username'}<input value={username} onChange={(event) => setUsername(event.target.value)} autoComplete="username" /></label><label>{russian ? 'Пароль' : 'Password'}<input type="password" value={password} onChange={(event) => setPassword(event.target.value)} autoComplete="current-password" /></label><button className="action-button">{russian ? 'Войти' : 'Sign in'}</button>{error && <p className="api-state api-state--error">{error}</p>}</form><p className="login-gate__note">{russian ? 'Только исследовательский прототип. Промышленная аутентификация и корпоративная интеграция идентификации находятся за рамками текущей версии.' : 'Development prototype only. Production authentication and corporate identity integration are out of scope.'}</p></section></main>;
}

export default LoginGate;
