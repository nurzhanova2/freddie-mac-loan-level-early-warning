# Этап 12. Persistent audit trail и экспертный workflow

## Workflow

```text
Alert Queue → Alert Detail → expert decision/comment
            → POST /api/v1/alerts/{alert_id}/reviews
            → expert_reviews + audit_events (PostgreSQL)
```

После успешного POST alert получает статус `Reviewed`; одновременно создаются
связанные `expert_reviews` и `audit_events` записи. Audit event фиксирует
actor, тип события, момент времени, decision/comment и связанные версии
модели/данных.

## API

- `POST /api/v1/alerts/{alert_id}/reviews` — создать expert review;
- `GET /api/v1/audit-events` — получить persistent audit trail.

В текущем development release actor имеет имя `demo_risk_analyst`. Это
контролируемая демонстрационная заглушка, а не authentication mechanism. До
подключения реальных записей необходимы настоящий identity provider, RBAC и
защищённое хранение secrets.
