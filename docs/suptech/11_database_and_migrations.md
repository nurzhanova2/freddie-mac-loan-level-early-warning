# Этап 11. База данных и миграции

## Сервис

В Docker Compose добавлен `suptech-db` на PostgreSQL 16 с отдельным persistent
volume `suptech_postgres_data`. API ожидает готовность БД и применяет Alembic
migration `20260921_0001` перед стартом.

## Таблицы

| Таблица | Назначение |
|---|---|
| `users` | роли участников review workflow |
| `data_versions` | версия и classification витрины данных |
| `model_versions` | registry моделей и validation summary |
| `model_runs` | связь запуска с версией модели и данных |
| `alerts` | минимальные безопасные alert DTO |
| `expert_reviews` | решения и комментарии экспертов |
| `audit_events` | неизменяемые события audit trail |

При первом запуске API seed-логика создаёт только synthetic demo records,
demo user и model/data version. Она не читает каталог `fannie_mae/data`.

## Локальная конфигурация

Значения для локальной разработки определены через безопасные defaults в
Compose. При необходимости их можно переопределить в локальном `.env`,
созданном из `.env.example`. `.env` исключён из Git.
