export const evidence = {
  ru: {
    overview: { title: 'Объяснимый искусственный интеллект для раннего выявления кредитного риска и скрытого ухудшения качества заёмщика', cards: [['Исследовательский пробел', 'Сохраняют ли модели раннего предупреждения на уровне кредита различающую способность, калибровку, lead time и устойчивость объяснений при временном и когортном сдвиге?'], ['Цель исследования', 'Разработать и валидировать объяснимую модель раннего предупреждения, выявляющую ухудшение качества заёмщика до формальной просрочки.'], ['Научный вклад', 'Калиброванный SHAP-объяснимый XGBoost оценён вне периода обучения и между когортами Q1–Q3 с учётом lead time и устойчивости объяснений.']], flow: ['Данные', 'Score', 'Alert', 'Объяснение', 'Risk trigger', 'Экспертная проверка'] },
    dataset: { title: 'Обзор данных', kpis: [['467,6 млн', 'наблюдений «кредит–месяц»'], ['8,27 млн', 'кредитов в панелях когорт'], ['16', 'когорт Q1 и Q3'], ['2006–2024', 'годы выдачи'], ['2', 'исхода на горизонте 6 месяцев']], coverage: [{ cohort: 'Q1 cohorts', loans: '3 343 420', rows: '185 931 842', share: '39,8%' }, { cohort: 'Q3 cohorts', loans: '4 929 119', rows: '281 706 562', share: '60,2%' }, { cohort: 'Всего', loans: '8 272 539', rows: '467 638 404', share: '100,0%' }] },
    design: { title: 'Дизайн исследования', leakage: 'Из набора признаков исключены servicing-поля, доступные только после окна исхода, включая признаки foreclosure, loss severity и post-default modification. Это предотвращает look-ahead bias.', outcomes: [['Formal adverse', '90+ DPD в течение шести месяцев после отчётного месяца.'], ['Early deterioration', 'Переход к 30+ DPD в течение шести месяцев, отражающий скрытое ухудшение до формальной просрочки.']] },
  },
  en: {
    overview: { title: 'Explainable AI for Early Identification of Credit Risk and Latent Borrower Deterioration', cards: [['Research gap', 'Can loan-level early-warning models preserve discrimination, calibration, lead time and explanation stability under temporal and cohort shift?'], ['Research objective', 'Develop and validate an explainable early-warning model that identifies borrower deterioration ahead of formal delinquency.'], ['Research contribution', 'A calibrated SHAP-explainable XGBoost is evaluated out of time and across Q1–Q3 cohorts with lead-time and explanation-stability evidence.']], flow: ['Data', 'Score', 'Alert', 'Explanation', 'Risk trigger', 'Expert review'] },
    dataset: { title: 'Dataset Overview', kpis: [['467.6M', 'loan-month observations'], ['8.27M', 'loans across cohort panels'], ['16', 'Q1 and Q3 cohorts'], ['2006–2024', 'acquisition years'], ['2', 'six-month outcomes']], coverage: [{ cohort: 'Q1 cohorts', loans: '3,343,420', rows: '185,931,842', share: '39.8%' }, { cohort: 'Q3 cohorts', loans: '4,929,119', rows: '281,706,562', share: '60.2%' }, { cohort: 'Total', loans: '8,272,539', rows: '467,638,404', share: '100.0%' }] },
    design: { title: 'Research Design', leakage: 'Servicing fields observable only after the outcome window, including foreclosure, loss severity and post-default modification fields, are excluded to prevent look-ahead bias.', outcomes: [['Formal adverse', '90+ DPD within six months after the reporting month.'], ['Early deterioration', 'Transition to 30+ DPD within six months, capturing latent deterioration ahead of formal delinquency.']] },
  },
};

export const modelRows = [
  { model: 'Logistic Regression', target: 'Formal adverse', roc: '0.8794', pr: '0.1879', rate: '0.4849%' },
  { model: 'XGBoost', target: 'Formal adverse', roc: '0.8943', pr: '0.2866', rate: '0.4849%' },
  { model: 'Logistic Regression', target: 'Early deterioration', roc: '0.7254', pr: '0.0596', rate: '2.3380%' },
  { model: 'XGBoost', target: 'Early deterioration', roc: '0.7310', pr: '0.0663', rate: '2.3380%' },
];

export const trainingSizeEvidence = {
  ru: {
    title: 'Чувствительность к объёму исторических данных',
    caption: 'Независимая Q1 OOT-проверка natural-rate XGBoost; модель и калибратор были зафиксированы до оценки.',
    rows: [
      { target: 'Formal adverse', sample: '1% · 622 812', roc: '0,8788', brier: '0,004034', precision: '24,84%', conclusion: 'кандидат для ресурсного переобучения' },
      { target: 'Formal adverse', sample: '25% · 15 576 478', roc: '0,8926', brier: '0,004146', precision: '24,03%', conclusion: 'ROC-AUC выше; operational-выигрыш неустойчив' },
      { target: 'Early deterioration', sample: '1% · 609 823', roc: '0,7274', brier: '0,022471', precision: '8,81%', conclusion: 'кандидат для ресурсного переобучения' },
      { target: 'Early deterioration', sample: '25% · 15 251 786', roc: '0,7309', brier: '0,022545', precision: '8,44%', conclusion: 'ROC-AUC выше; operational-выигрыш неустойчив' },
    ],
    note: 'В пределах проверенного Q1-контура 1% natural-rate train сохраняет конкурентное качество, лучший Brier score и максимальную точность фиксированных очередей. Это исследовательский ориентир, требующий подтверждения на Q3 и Freddie Mac; он не заменяет зарегистрированную модель и не меняет alert policy автоматически.',
  },
  en: {
    title: 'Sensitivity to historical training volume',
    caption: 'Independent Q1 OOT evaluation of natural-rate XGBoost; models and calibrators were frozen before assessment.',
    rows: [
      { target: 'Formal adverse', sample: '1% · 622,812', roc: '0.8788', brier: '0.004034', precision: '24.84%', conclusion: 'resource-efficient retraining candidate' },
      { target: 'Formal adverse', sample: '25% · 15,576,478', roc: '0.8926', brier: '0.004146', precision: '24.03%', conclusion: 'higher ROC-AUC; no stable operational gain' },
      { target: 'Early deterioration', sample: '1% · 609,823', roc: '0.7274', brier: '0.022471', precision: '8.81%', conclusion: 'resource-efficient retraining candidate' },
      { target: 'Early deterioration', sample: '25% · 15,251,786', roc: '0.7309', brier: '0.022545', precision: '8.44%', conclusion: 'higher ROC-AUC; no stable operational gain' },
    ],
    note: 'Within the tested Q1 contour, 1% natural-rate training retains competitive quality, the best Brier score, and the highest fixed-queue precision. This is a research benchmark requiring confirmation on Q3 and Freddie Mac; it does not replace the registered model or automatically change alert policy.',
  },
};
