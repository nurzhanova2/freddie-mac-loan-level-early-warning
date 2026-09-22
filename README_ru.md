# Explainable SupTech Early-Warning Research Prototype

Исследовательский прототип для диссертации по объяснимому искусственному
интеллекту в кредитном риске. Он представляет результаты Fannie Mae в виде
контролируемого процесса:

`data → score → alert → explanation → risk trigger → expert review`

Прототип не является производственной банковской или надзорной системой и не
принимает автоматических решений по кредитам.

## Быстрый запуск

Требуется Docker Desktop. Из корня репозитория выполните:

```bash
docker compose up --build
```

После запуска откройте:

| Компонент | Адрес | Назначение |
| --- | --- | --- |
| Web-интерфейс | http://localhost:5173 | Панель исследования и SupTech-инструмент |
| API documentation | http://localhost:8000/docs | Swagger-интерфейс FastAPI |
| PostgreSQL | `localhost:5432` | Локальное хранилище пользователей и audit trail |

## Вход в систему

На странице входа выберите язык **RU / EN**, укажите логин и пароль. Для всех
демонстрационных учётных записей используется один пароль:

```text
demo-password-change-me
```

| Роль | Логин | Доступ и сценарий проверки |
| --- | --- | --- |
| Research viewer | `demo_research_viewer` | Просмотр научных результатов, dashboard, очереди и карточек alerts; создание expert review запрещено. |
| Risk analyst | `demo_risk_analyst` | Все возможности viewer и сохранение решения эксперта по alert в audit trail. |
| Model governance | `demo_model_governance` | Alerts, Model Governance, registry, audit trail, создание и изменение локальных пользователей. |
| Data steward | `demo_data_steward` | Alerts, Model Governance, registry и audit trail; без управления пользователями. |
| Platform administrator | `demo_platform_admin` | Научные результаты и административный контур: создание, смена роли и деактивация локальных пользователей. Доступ к alert-данным намеренно не выдаётся. |

Для смены роли нажмите **«Выйти»** в правой части шапки и войдите под другой
учётной записью.

## Как пользоваться прототипом

### 1. Научные результаты

В разделе **«Научные результаты / Research Evidence»** доступны:

- описание Fannie Mae когорт Q1 и Q3;
- дизайн временной валидации;
- сравнение моделей и ключевые метрики;
- устойчивость между когортами и SHAP-результаты;
- выводы исследования.

### 2. Система раннего предупреждения

В разделе **«Система раннего предупреждения / Early-Warning System»**:

1. Откройте **«Очередь сигналов»** и отфильтруйте Red/Amber alerts или статус review.
2. Выберите сигнал, затем откройте **«Карточку сигнала»**.
3. Просмотрите risk score, trigger threshold, версию модели, версию данных и
   локальное SHAP-объяснение.
4. Под ролью `risk_analyst` или `model_governance` сохраните решение эксперта:
   *Priority follow-up*, *Watchlist*, *Monitoring* или *No immediate action*.
5. Под ролью `model_governance` или `data_steward` проверьте появление события
   в **Model Governance → Audit trail**.

### 3. Администрирование

Раздел **Administration** доступен `model_governance` и `platform_admin`.
Он позволяет создать локального пользователя, выдать или изменить роль,
деактивировать учётную запись и указать причину изменения.

Защитные правила workflow:

- пользователь не может изменить собственную роль или активность;
- изменение доступа требует причины и подтверждения;
- нельзя понизить или деактивировать последнего активного `platform_admin`;
- деактивированная учётная запись не может войти вновь;
- события `user_created` и `user_access_updated` сохраняются в `audit_events`.

## Данные и безопасность

По умолчанию API использует синтетические демонстрационные alerts. Интерфейс
браузера получает только безопасный alert DTO: score, tier, cohort, дату
наблюдения, объясняющий фактор SHAP и версии модели/данных.

В браузер **никогда не передаются** raw Fannie Mae файлы, стабильные loan IDs,
полные feature vectors или обучающие выборки. Подключение реальной
исследовательской витрины допускается только через предварительно разрешённый
CSV export и серверный adapter. Подробности — в
[контракте данных](docs/suptech/09_data_contract_and_access_policy.md) и
[архитектурной документации](docs/suptech/README.md).

## Проверка разработки

```bash
npm run test:ui
python3 -m unittest tests.api.test_live_api tests.api.test_score_export_adapter
npm run build
```

## Структура репозитория

```text
src/
├── common/               # общие provider-neutral компоненты
├── fannie_mae/           # Fannie Mae research pipeline
├── freddie_mac/          # Freddie Mac ingestion и preparation
└── prototype/            # React UI, FastAPI, PostgreSQL audit trail

fannie_mae/               # данные, модели, отчёты и документация Fannie Mae
freddie_mac/              # данные, отчёты и документация Freddie Mac
tests/                    # API и frontend policy tests
```

Два провайдера не объединяются в одну обучающую таблицу: активная модель
использует Fannie Mae, а Freddie Mac сохраняется как независимый источник для
будущей проверки переносимости.
