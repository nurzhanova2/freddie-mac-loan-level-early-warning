# Этап 9. Контракт данных и политика доступа

## 1. Цель

Контракт отделяет исследовательские Fannie Mae files от web-интерфейса.
Browser client никогда не получает raw acquisition/performance files, полные
panel tables, training samples или исходные устойчивые идентификаторы кредита.
Он получает лишь минимальный объект alert, сформированный серверным adapter.

## 2. Разрешённый alert DTO

| Поле | Назначение | Допустимо в browser client |
|---|---|---|
| `alert_id` | технический идентификатор сигнала | да |
| `loan_reference` | псевдонимизированная ссылка | да |
| `reporting_month`, `cohort` | временной и когортный контекст | да |
| `target`, `risk_score`, `trigger_threshold`, `tier` | результат модели и trigger policy | да |
| `top_shap_driver`, `top_shap_contribution` | локальное объяснение | да |
| `model_version`, `data_version` | воспроизводимость | да |
| `review_status`, `expert_decision` | workflow review | да |
| raw loan ID, full servicing history, full feature vector | исходные/избыточные данные | нет |
| raw archive path, training row, protected source file | внутренняя research infrastructure | нет |

## 3. Роли

| Роль | Доступ |
|---|---|
| `research_viewer` | агрегированные метрики, очередь и минимальная карточка alert |
| `risk_analyst` | всё `research_viewer` + создание экспертного review |
| `model_governance` | registry моделей, policy versions, audit trail |
| `data_steward` | server-side preparation и утверждённые витрины; не передаёт raw files браузеру |

Этап 9 не реализует authentication. Роли являются проектной политикой и будут
привязаны к auth provider до подключения реальных записей.

## 4. Запреты

1. Нельзя возвращать raw Fannie Mae files через HTTP API.
2. Нельзя использовать настоящий loan ID как URL-параметр или browser state.
3. Нельзя выдавать полный набор признаков, training samples или исходные
   записи ради удобства интерфейса.
4. Нельзя принять автоматическое решение только на основании `tier` или score.
5. До внедрения authentication и persistent audit trail реальный data adapter
   остаётся отключённым.

## 5. Классификация текущего API

Текущая API версия предоставляет исключительно synthetic demo data и прямо
маркирует ответ как `synthetic_demo_only`. Она не является каналом доступа к
Fannie Mae data.
