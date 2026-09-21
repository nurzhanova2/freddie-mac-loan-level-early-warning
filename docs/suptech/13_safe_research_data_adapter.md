# Этап 13. Безопасный adapter к исследовательским данным

## Принцип

API не читает `fannie_mae/data/raw`, interim/processed panels или model
samples. Он принимает только заранее подготовленный approved alert-score CSV,
который оператор явно монтирует server-side и указывает через
`SUPTECH_APPROVED_ALERT_EXPORT`.

## Валидация adapter

Adapter:

1. принимает только CSV внутри `SUPTECH_APPROVED_EXPORTS_ROOT`;
2. требует минимальные разрешённые поля alert DTO;
3. отклоняет поля-маркеры raw данных (`loan_id`, `raw_path`,
   `feature_vector`, `training_sample`, `servicing_history`);
4. преобразует только score/threshold/SHAP contribution;
5. передаёт React исключительно API DTO.

Если export не настроен, сервис использует `synthetic_demo_only` seed. Это
безопасный default. Чтобы сменить режим на `approved_research_export`, нужно
отдельно подготовить и утвердить витрину; adapter намеренно не умеет читать
исходные Fannie Mae archives.

## Формат approved export

Разрешены только поля из data contract: `alert_id`, `loan_reference`,
`cohort`, `reporting_month`, `target`, `risk_score`, `trigger_threshold`,
`tier`, `top_shap_driver`, `top_shap_contribution`, `review_status` и
необязательный `expert_decision`.
