export const screenGroups = [
  {
    id: 'research', label: 'Research Evidence', ruLabel: 'Научные результаты',
    screens: [
      { id: 'research-overview', title: 'Research Overview', ruTitle: 'Обзор исследования' },
      { id: 'research-dataset', title: 'Dataset Overview', ruTitle: 'Обзор данных' },
      { id: 'research-design', title: 'Research Design', ruTitle: 'Дизайн исследования' },
      { id: 'research-performance', title: 'Model Performance', ruTitle: 'Качество моделей' },
      { id: 'research-robustness', title: 'Robustness Across Cohorts', ruTitle: 'Устойчивость по когортам' },
      { id: 'research-conclusions', title: 'Research Conclusions', ruTitle: 'Выводы исследования' },
    ],
  },
  {
    id: 'ews', label: 'SupTech Early-Warning System', ruLabel: 'Система раннего предупреждения',
    screens: [
      { id: 'ews-dashboard', title: 'EWS Dashboard', ruTitle: 'Панель раннего предупреждения', roles: ['research_viewer', 'risk_analyst', 'model_governance', 'data_steward'] },
      { id: 'ews-alert-queue', title: 'Alert Queue', ruTitle: 'Очередь сигналов', roles: ['research_viewer', 'risk_analyst', 'model_governance', 'data_steward'] },
      { id: 'ews-alert-detail', title: 'Alert Detail', ruTitle: 'Карточка сигнала', roles: ['research_viewer', 'risk_analyst', 'model_governance', 'data_steward'] },
      { id: 'ews-risk-monitoring', title: 'Risk Monitoring', ruTitle: 'Мониторинг риска', roles: ['research_viewer', 'risk_analyst', 'model_governance', 'data_steward'] },
      { id: 'ews-governance', title: 'Model Governance', ruTitle: 'Управление моделью', roles: ['model_governance', 'data_steward'] },
      { id: 'ews-administration', title: 'Administration', ruTitle: 'Администрирование', roles: ['model_governance', 'platform_admin'] },
    ],
  },
];
