# Перечень таблиц и рисунков

Перечень является единым реестром нумерации для основной версии диссертации.
Номер, подпись и ссылка в тексте должны совпадать с данной записью. Ссылки
ведут на воспроизводимые артефакты проекта.

## Таблицы

| Номер | Подпись | Артефакт |
|---|---|---|
| Таблица 2.1 | Покрытие Q1-когорт Fannie Mae | [CSV](../../../reports/eda_v01/01_cohort_overview.csv) |
| Таблица 2.2 | Характеристики кредитов на дату выдачи по когортам | [CSV](../../../reports/eda_v01/03_origination_characteristics.csv) |
| Таблица 3.1 | Шестимесячные исходы по Q1-когортам | [CSV](../../../reports/eda_v01/05_six_month_outcome_summary.csv) |
| Таблица 3.2 | Распределение текущего статуса просрочки | [CSV](../../../reports/eda_v01/04_current_delinquency_distribution.csv) |
| Таблица 3.3 | Сопоставление одинаковых Q1- и Q3-когорт | [CSV](../../../reports/q1_q3_robustness_v01/02_matched_q1_q3_comparison.csv) |
| Таблица 4.1 | Временное разделение train, validation и out-of-time | [CSV](../../../reports/splits/fannie_temporal_split_v01_summary.csv) |
| Таблица 4.2 | Показатели логистической базовой модели | [CSV](../../../reports/models/logistic_baseline_v01_summary.csv) |
| Таблица 4.3 | Сравнение вероятностной калибровки | [CSV](../../../reports/models/logistic_isotonic_calibration_v01_summary.csv) |
| Таблица 4.4 | Чувствительность OOT-метрик к размеру natural-rate train | [CSV](../../../reports/train_size_sensitivity_v01/train_size_oot_metrics_summary_v01.csv) |
| Таблица 4.5 | Сопоставление горизонтов 3, 6 и 12 месяцев на общем OOT | [CSV](../../../reports/horizon_sensitivity_v01/horizon_oot_comparability_summary_v01.csv) |
| Таблица 4.6 | Validation-only сопоставление кандидатов tree-моделей | [CSV](../../../reports/tree_hyperparameter_selection_v01/tree_validation_candidate_comparison_v01.csv) |
| Таблица 4.7 | Конфигурации tree-моделей, выбранные на validation | [CSV](../../../reports/tree_hyperparameter_selection_v01/tree_validation_overall_selection_v01.csv) |
| Таблица 4.8 | Калиброванная OOT-проверка tree-моделей и registry-решение | [CSV](../../../reports/tree_hyperparameter_selection_v01/tree_oot_governance_decision_v01.csv) |
| Таблица 5.1 | Глобальная SHAP-важность для formal adverse | [CSV](../../../reports/models/formal_adverse_6m_xgboost_shap_global_v01.csv) |
| Таблица 5.2 | Permutation importance formal adverse на validation | [CSV](../../../reports/xai_extension_v01/formal_adverse_6m_validation_permutation_importance_v01.csv) |
| Таблица 5.3 | Permutation importance раннего ухудшения на validation | [CSV](../../../reports/xai_extension_v01/early_deterioration_6m_validation_permutation_importance_v01.csv) |
| Таблица 5.4 | Стабильность SHAP-объяснений Red и Amber между группами когорт | [CSV](../../../reports/xai_extension_v01/xai_alert_cohort_shap_audit_summary_v01.csv) |
| Таблица 6.1 | Сравнение Logistic Regression и XGBoost | [CSV](../../../reports/models/final_model_comparison_v01.csv) |
| Таблица 6.2 | Итоговые метрики моделей и trigger policy | [CSV](../../../reports/models/final_dissertation_summary_v01.csv) |
| Таблица A.1 | Параметры моделей, калибровка и alert-пороги | [Приложение А](appendix_a_methodological_audit.md) |
| Таблица Б.1 | Data lineage от архивной поставки до безопасного alert-export | [Приложение Б](appendix_b_data_lineage_and_glossary.md) |
| Таблица Б.2 | Рабочий глоссарий данных, исходов и сигналов | [Приложение Б](appendix_b_data_lineage_and_glossary.md) |

## Рисунки

| Номер | Подпись | Артефакт |
|---|---|---|
| Рисунок 2.1 | Характеристики выдачи по Q1-когортам | [PNG](../../../reports/figures/eda_v01/03_origination_characteristics_trend.png) |
| Рисунок 3.1 | Шестимесячные частоты исходов по Q1-когортам | [PNG](../../../reports/figures/eda_v01/01_six_month_outcome_rates_by_cohort.png) |
| Рисунок 3.2 | Распределение текущих статусов просрочки | [PNG](../../../reports/figures/eda_v01/02_current_delinquency_distribution.png) |
| Рисунок 3.3 | Календарная динамика текущей просрочки | [PNG](../../../reports/figures/eda_v01/05_calendar_month_delinquency_trend.png) |
| Рисунок 3.4 | Сопоставление шестимесячных исходов Q1 и Q3 | [PNG](../../../reports/figures/q1_q3_robustness_v01/01_q1_q3_outcome_comparison.png) |
| Рисунок 4.1 | Хронологическое разделение выборки | [PNG](../../../reports/figures/splits/fannie_temporal_split_timeline_v01.png) |
| Рисунок 4.2 | Калибровка вероятностей formal adverse | [PNG](../../../reports/figures/models/formal_adverse_6m_calibration_v01.png) |
| Рисунок 4.3 | Калибровка вероятностей раннего ухудшения | [PNG](../../../reports/figures/models/early_deterioration_6m_calibration_v01.png) |
| Рисунок 4.4 | OOT-метрики formal adverse в зависимости от размера train | [PNG](../../../reports/figures/train_size_sensitivity_v01/formal_adverse_6m_train_size_oot_metrics_v01.png) |
| Рисунок 4.5 | OOT-метрики раннего ухудшения в зависимости от размера train | [PNG](../../../reports/figures/train_size_sensitivity_v01/early_deterioration_6m_train_size_oot_metrics_v01.png) |
| Рисунок 4.6 | OOT-калибровка formal adverse по размерам train | [PNG](../../../reports/figures/train_size_sensitivity_v01/formal_adverse_6m_train_size_oot_calibration_v01.png) |
| Рисунок 4.7 | OOT-калибровка раннего ухудшения по размерам train | [PNG](../../../reports/figures/train_size_sensitivity_v01/early_deterioration_6m_train_size_oot_calibration_v01.png) |
| Рисунок 4.8 | Нормированное OOT-сопоставление горизонтов formal adverse | [PNG](../../../reports/figures/horizon_sensitivity_v01/formal_adverse_horizon_oot_comparability_v01.png) |
| Рисунок 4.9 | Нормированное OOT-сопоставление горизонтов раннего ухудшения | [PNG](../../../reports/figures/horizon_sensitivity_v01/early_deterioration_horizon_oot_comparability_v01.png) |
| Рисунок 4.10 | OOT-калибровка tree-моделей для formal adverse | [PNG](../../../reports/figures/tree_hyperparameter_selection_v01/formal_adverse_6m_oot_reliability_v01.png) |
| Рисунок 4.11 | OOT-калибровка tree-моделей для раннего ухудшения | [PNG](../../../reports/figures/tree_hyperparameter_selection_v01/early_deterioration_6m_oot_reliability_v01.png) |
| Рисунок 5.1 | Глобальная SHAP-важность formal adverse | [PNG](../../../reports/figures/models/formal_adverse_6m_xgboost_shap_global_v01.png) |
| Рисунок 5.2 | Сопоставление SHAP-факторов Q1 и Q3 для formal adverse | [PNG](../../../reports/figures/q3_shap_v01/formal_adverse_6m_q1_q3_shap_comparison_v01.png) |
| Рисунок 5.3 | ALE-профили formal adverse на validation | [PNG](../../../reports/figures/xai_extension_v01/formal_adverse_6m_validation_ale_v01.png) |
| Рисунок 5.4 | ALE-профили раннего ухудшения на validation | [PNG](../../../reports/figures/xai_extension_v01/early_deterioration_6m_validation_ale_v01.png) |
| Рисунок 5.5 | SHAP-сравнение Red сигналов: стрессовые и референтные когорты | [PNG](../../../reports/figures/xai_extension_v01/formal_adverse_6m_alert_cohort_shap_comparison_v01.png) |
| Рисунок 5.6 | SHAP-сравнение Amber сигналов: стрессовые и референтные когорты | [PNG](../../../reports/figures/xai_extension_v01/early_deterioration_6m_alert_cohort_shap_comparison_v01.png) |
| Рисунок 6.1 | Итоговое сопоставление модели и trigger policy | [PNG](../../../reports/figures/final_v01/final_model_and_trigger_summary_v01.png) |

## Правило ссылок в тексте

Используется форма «см. рисунок 3.4» или «результаты представлены в таблице
6.1». Подпись располагается под рисунком и над таблицей. В подписи указывается
содержательное название без имени файла; источник формулируется как «расчёты
автора по данным Fannie Mae» с указанием версии артефакта в приложении или
сноске.

Методологические определения и data lineage вынесены в [приложения А–Б](appendix_a_methodological_audit.md).
