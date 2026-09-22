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
      { id: 'ews-dashboard', title: 'EWS Dashboard', ruTitle: 'Панель раннего предупреждения', roles: screenRoles['ews-dashboard'] },
      { id: 'ews-alert-queue', title: 'Alert Queue', ruTitle: 'Очередь сигналов', roles: screenRoles['ews-alert-queue'] },
      { id: 'ews-alert-detail', title: 'Alert Detail', ruTitle: 'Карточка сигнала', roles: screenRoles['ews-alert-detail'] },
      { id: 'ews-risk-monitoring', title: 'Risk Monitoring', ruTitle: 'Мониторинг риска', roles: screenRoles['ews-risk-monitoring'] },
      { id: 'ews-governance', title: 'Model Governance', ruTitle: 'Управление моделью', roles: screenRoles['ews-governance'] },
      { id: 'ews-administration', title: 'Administration', ruTitle: 'Администрирование', roles: screenRoles['ews-administration'] },
    ],
  },
];
import { screenRoles } from './accessPolicy.js';
