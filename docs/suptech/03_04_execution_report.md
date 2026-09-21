# Этапы 3–4. Основная оболочка и Research Evidence

## Выполнено

1. Реализована общая browser-layout оболочка: фиксированный sidebar, верхняя
   информационная панель, переключатель RU/EN и адаптивная сетка. Навигация
   содержит полный перечень экранов Research Evidence и будущего EWS.
2. Реализованы шесть экранов Research Evidence: обзор, данные, дизайн,
   качество моделей, устойчивость между когортами и выводы.
3. На экранах показаны только проверенные агрегированные результаты: объём
   панелей Q1+Q3, временное разделение, anti-leakage policy, out-of-time
   метрики Logistic Regression/XGBoost, trigger results и SHAP stability.
4. Графики реализованы как лёгкие SVG/CSS компоненты без копирования
   защищённых loan-level данных в фронтенд.

## Источники значений

- `fannie_mae/reports/models/final_model_comparison_v01.csv`;
- `fannie_mae/reports/models/final_dissertation_summary_v01.csv`;
- `fannie_mae/reports/q1_q3_robustness_v01/01_q1_q3_cohort_summary.csv`;
- `fannie_mae/reports/q1_q3_robustness_v01/02_matched_q1_q3_comparison.csv`.

## Проверка

`npm run build` завершён успешно. React UI доступен через Docker Compose по
`http://localhost:5173`.

## Граница этапа

EWS-страницы навигационно доступны, но сознательно показывают placeholder:
очередь signals, карточка alert, monitoring и governance будут построены на
этапах 5–7 поверх synthetic demo dataset и будущего audit-trail contract.
