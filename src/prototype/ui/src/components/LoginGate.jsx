import { useState } from 'react';
import { api, isStaticDemo } from '../data/apiClient.js';

function LoginGate({ language, onLanguageChange, onAuthenticated }) {
  const [username, setUsername] = useState('demo_risk_analyst');
  const [password, setPassword] = useState('demo-password-change-me');
  const [passwordVisible, setPasswordVisible] = useState(false);
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
        <div className="login-brand"><span className="login-brand__mark" aria-hidden="true">↗</span><p className="section-label">{russian ? 'Контролируемый исследовательский доступ' : 'Controlled research access'}</p></div>
        <div className="language-switch" aria-label={russian ? 'Язык интерфейса' : 'Interface language'}><button className={russian ? 'is-active' : ''} type="button" onClick={() => onLanguageChange('ru')}>RU</button><button className={!russian ? 'is-active' : ''} type="button" onClick={() => onLanguageChange('en')}>EN</button></div>
      </header>
      <h1 id="login-title">{russian ? 'Платформа SupTech-исследований' : 'SupTech Research Platform'}</h1>
      <p className="login-gate__lede">{russian ? 'Войдите в локальный прототип, чтобы открыть разрешённые исследовательские и управленческие разделы.' : 'Sign in to the local prototype to open permitted research and governance views.'}</p>
      {isStaticDemo && <p className="login-gate__public-demo">{russian ? 'Публичная демонстрация: используются только синтетические безопасные записи; изменения хранятся лишь в этом браузере.' : 'Public demonstration: only synthetic safe records are used; changes remain in this browser only.'}</p>}
      <form onSubmit={submit} aria-describedby="login-boundary">
        <label>{russian ? 'Логин' : 'Username'}<input value={username} onChange={(event) => setUsername(event.target.value)} autoComplete="username" autoFocus required /></label>
        <label>{russian ? 'Пароль' : 'Password'}<span className="login-password-field"><input type={passwordVisible ? 'text' : 'password'} value={password} onChange={(event) => setPassword(event.target.value)} autoComplete="current-password" required /><button type="button" className="login-password-toggle" aria-label={passwordVisible ? (russian ? 'Скрыть пароль' : 'Hide password') : (russian ? 'Показать пароль' : 'Show password')} aria-pressed={passwordVisible} onClick={() => setPasswordVisible((visible) => !visible)}><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M2.5 12s3.5-5.5 9.5-5.5S21.5 12 21.5 12s-3.5 5.5-9.5 5.5S2.5 12 2.5 12Z" /><circle cx="12" cy="12" r="2.5" /></svg></button></span></label>
        <button className="action-button login-submit" disabled={isSubmitting}><span>{isSubmitting ? (russian ? 'Выполняется вход…' : 'Signing in…') : (russian ? 'Войти' : 'Sign in')}</span><span aria-hidden="true">→</span></button>
        {error && <p className="api-state api-state--error" role="alert">{error}</p>}
      </form>
      <aside className="login-boundary" id="login-boundary"><span className="login-boundary__icon" aria-hidden="true">ⓘ</span><div><p className="card-kicker">{russian ? 'Граница доступа' : 'Access boundary'}</p><p>{russian ? 'Роль назначается администратором после создания локальной учётной записи. Вход не позволяет самостоятельно изменить роль пользователя.' : 'A platform administrator assigns the role after the local account is created. Signing in cannot change a user role.'}</p></div></aside>
      <p className="login-gate__note">{russian ? 'Только исследовательский прототип. Промышленная аутентификация и корпоративная интеграция идентификации не входят в текущую версию.' : 'Development prototype only. Production authentication and corporate identity integration are out of scope.'}</p>
    </section>
  </main>;
}

export default LoginGate;
