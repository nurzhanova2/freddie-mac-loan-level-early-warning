import { useState } from 'react';
import { api } from '../data/apiClient.js';

function LoginGate({ language, onLanguageChange, onAuthenticated }) {
  const [username, setUsername] = useState('demo_risk_analyst');
  const [password, setPassword] = useState('demo-password-change-me');
  const [error, setError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const russian = language === 'ru';
  async function submit(event) {
    event.preventDefault();
    setError('');
    setIsSubmitting(true);
    try {
      const result = await api.login(username, password);
      sessionStorage.setItem('suptech_access_token', result.access_token);
      sessionStorage.setItem('suptech_role', result.role);
      sessionStorage.setItem('suptech_username', result.username);
      onAuthenticated({ username: result.username, role: result.role });
    } catch {
      setError(russian ? 'Не удалось выполнить вход. Проверьте логин и пароль локальной учётной записи.' : 'Login failed. Check the local development credentials.');
    } finally {
      setIsSubmitting(false);
    }
  }
  return <main className="login-gate">
    <section className="login-card" aria-labelledby="login-title">
      <header className="login-gate__heading">
        <div className="login-brand"><span className="login-brand__mark" aria-hidden="true">↗</span><div><p className="section-label">{russian ? 'Контролируемый исследовательский доступ' : 'Controlled research access'}</p><h1 id="login-title">{russian ? 'Платформа SupTech-исследований' : 'SupTech Research Platform'}</h1></div></div>
        <div className="language-switch" aria-label={russian ? 'Язык интерфейса' : 'Interface language'}><button className={russian ? 'is-active' : ''} type="button" onClick={() => onLanguageChange('ru')}>RU</button><button className={!russian ? 'is-active' : ''} type="button" onClick={() => onLanguageChange('en')}>EN</button></div>
      </header>
      <p className="login-gate__lede">{russian ? 'Войдите в локальный прототип, чтобы открыть разрешённые исследовательские и governance-экраны.' : 'Sign in to the local prototype to open permitted research and governance views.'}</p>
      <form onSubmit={submit} aria-describedby="login-boundary">
        <label>{russian ? 'Логин' : 'Username'}<input value={username} onChange={(event) => setUsername(event.target.value)} autoComplete="username" autoFocus required /></label>
        <label>{russian ? 'Пароль' : 'Password'}<input type="password" value={password} onChange={(event) => setPassword(event.target.value)} autoComplete="current-password" required /></label>
        <button className="action-button" disabled={isSubmitting}>{isSubmitting ? (russian ? 'Выполняется вход…' : 'Signing in…') : (russian ? 'Войти' : 'Sign in')}</button>
        {error && <p className="api-state api-state--error" role="alert">{error}</p>}
      </form>
      <aside className="login-boundary" id="login-boundary"><p className="card-kicker">{russian ? 'Граница доступа' : 'Access boundary'}</p><p>{russian ? 'Роль назначается администратором платформы после создания локальной учётной записи. Вход не позволяет самостоятельно изменить роль.' : 'A platform administrator assigns the role after the local account is created. Signing in cannot change a user role.'}</p></aside>
      <p className="login-gate__note">{russian ? 'Только исследовательский прототип. Промышленная аутентификация и корпоративная интеграция идентификации находятся за рамками текущей версии.' : 'Development prototype only. Production authentication and corporate identity integration are out of scope.'}</p>
    </section>
  </main>;
}

export default LoginGate;
