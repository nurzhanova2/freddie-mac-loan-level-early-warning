# Этапы 14–15. Frontend integration, тестирование и Docker Compose

## Интеграция

React EWS больше не использует локальный `demoAlerts` adapter. Он обращается к
`VITE_API_BASE_URL` и получает через API:

- overview metrics для EWS Dashboard;
- alerts с filters по tier/review status и client-side search;
- Alert Detail и SHAP explanation;
- `POST` review в PostgreSQL;
- model registry и persistent audit trail.

Показаны состояния загрузки и ошибки API. Исследовательский раздел с
результатами диссертации остаётся статичным и воспроизводимым.

## Compose-архитектура

```text
Browser → React web :5173 → FastAPI :8000 → PostgreSQL :5432
                             │
                             └→ approved alert-score export (server-side only)
```

Одна команда запускает все компоненты:

```bash
docker compose up --build
```

## API integration tests

Добавлен [test_live_api.py](../../../tests/api/test_live_api.py). После
запуска Compose он проверяет, что contract не разрешает raw-data поля, что
фильтр alerts работает, а POST review создаёт persistent audit event:

```bash
python3 -m unittest tests.api.test_live_api
```

Тест пишет review только в локальную synthetic demo database.

## Граница текущего релиза

Authentication/RBAC, secrets management и включение approved real-data export
должны быть завершены до смены `synthetic_demo_only` режима. Поэтому текущий
полный стек остаётся безопасным dissertation research prototype.
