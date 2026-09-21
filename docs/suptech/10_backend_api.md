# Этап 10. Backend API

## Сервис

`suptech-api` — отдельный FastAPI-сервис. На данном шаге его endpoints
read-only и используют synthetic seed data. API служит стабильной границей
между React и будущими approved server-side data adapters.

## Endpoints

| Method | Endpoint | Назначение |
|---|---|---|
| GET | `/api/v1/health` | состояние сервиса и classification данных |
| GET | `/api/v1/contract` | API-version и разрешённые browser поля |
| GET | `/api/v1/alerts` | очередь с фильтрами `tier`, `review_status`, `limit` |
| GET | `/api/v1/alerts/{alert_id}` | минимальная карточка alert |
| GET | `/api/v1/alerts/{alert_id}/explanation` | локальное SHAP explanation |
| GET | `/api/v1/metrics/overview` | агрегированные EWS KPI |
| GET | `/api/v1/model-registry` | версия scoring model и governance metadata |

Ответы имеют обёртку с `api_version`, `data_classification` и `data`. Поле
`data_classification` сейчас всегда равно `synthetic_demo_only`.

## Локальный запуск

```bash
docker compose up --build
```

- UI: `http://localhost:5173`
- API docs: `http://localhost:8000/docs`
- health check: `http://localhost:8000/api/v1/health`

Persistent database, authentication, POST review endpoint и переключение на
approved real-data adapter не входят в этот этап.
