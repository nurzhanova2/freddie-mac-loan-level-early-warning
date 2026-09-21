# Этап 2. React-архитектура и запуск через Docker Compose

## 1. Структура

Интерфейс расположен в общем исходном корне проекта, отдельно от Fannie Mae и
Freddie Mac pipelines:

```text
src/prototype/ui/
├── index.html
├── src/
│   ├── app/          # composition root и манифест маршрутов
│   ├── components/   # переиспользуемые UI-компоненты
│   ├── data/         # демонстрационные adapters и contracts
│   ├── features/     # alert, review, governance и monitoring logic
│   ├── pages/        # экраны Research и EWS
│   └── styles/       # design tokens и глобальные правила
└── README.md
```

Такое размещение оставляет `src/fannie_mae` и `src/freddie_mac` независимыми
от интерфейса. На первом шаге фронтенд не содержит доступа к raw data,
обучающим выборкам или model artefacts.

## 2. Запуск

Единая команда разработки:

```bash
docker compose up --build
```

После запуска интерфейс доступен по адресу `http://localhost:5173`. Compose
монтирует рабочую копию проекта в контейнер, поэтому изменения React-кода
подхватываются development server без ручной пересборки. Для остановки:

```bash
docker compose down
```

## 3. Границы сервисов

В текущем релизе Compose поднимает один сервис `suptech-web`: это UI для
исследовательской демонстрации. API, база данных и отдельный worker будут
добавлены только когда появится необходимость хранить экспертные решения и
audit trail вне браузера. До этого состояния прототип остаётся статическим и
воспроизводимым.

## 4. Контракт следующего этапа

Экраны должны получать данные через adapters в `src/data`, а не напрямую из
Fannie Mae files. Это позволит позднее заменить synthetic demo data на API и
не переписывать представление. Поля контракта очереди: `alert_id`,
`synthetic_loan_id`, `reporting_month`, `risk_score`, `trigger_threshold`,
`alert_tier`, `top_shap_driver`, `model_version`, `data_version` и
`review_status`.
