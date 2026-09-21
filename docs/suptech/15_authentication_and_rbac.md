# Этап 15. Локальная авторизация и RBAC

## Реализация

Для dissertation research prototype реализована локальная development
authentication: `POST /api/v1/auth/login` выдаёт подписанный HMAC bearer token
на восемь часов. Пароли не хранятся открытым текстом: применяется PBKDF2-HMAC
SHA-256 с индивидуальной salt. В production такая схема должна быть заменена
на корпоративный identity provider/SSO и защищённое secrets management.

## Роли

| Роль | Разрешения |
|---|---|
| `research_viewer` | read-only очередь, карточки, explanations, metrics |
| `risk_analyst` | read-only доступ + создание expert review |
| `model_governance` | read-only доступ + review + registry и audit trail |
| `data_steward` | read-only доступ + registry и audit trail |

Health check и login остаются публичными; прочие endpoints требуют bearer
token. Политика защищает API, а не заменяет внешний контроль доступа к raw
data files.

## Development users

Локальные пользователи создаются автоматически при первом старте:
`demo_research_viewer`, `demo_risk_analyst`, `demo_model_governance`,
`demo_data_steward`. Пароль задаётся исключительно в локальном `.env` через
`SUPTECH_DEMO_PASSWORD`; пример находится в `.env.example`.

## Проверка

Интеграционные тесты проверяют успешный login, `401` без token, `403` для
viewer при попытке review, contract, persistent review и audit trail. Запуск:

```bash
python3 -m unittest tests.api.test_live_api tests.api.test_score_export_adapter
```
