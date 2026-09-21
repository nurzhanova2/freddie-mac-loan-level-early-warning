// Synthetic demonstration records only. No Fannie Mae borrower records are
// loaded into the browser interface.
export const demoAlerts = [
  ['ALT-2025-0001','DEMO-000001','2008Q1','2025-06','formal_adverse_6m',.782,.391,'Red','current_delinquency_status',.421,'Reviewed','Priority follow-up','90+ DPD',2],
  ['ALT-2025-0002','DEMO-000002','2020Q1','2025-06','formal_adverse_6m',.641,.391,'Red','original_interest_rate',.284,'In review','','Unobserved',null],
  ['ALT-2025-0003','DEMO-000003','2022Q1','2025-06','formal_adverse_6m',.578,.391,'Red','borrower_credit_score_at_origination',.233,'Reviewed','Watchlist','Unobserved',null],
  ['ALT-2025-0004','DEMO-000004','2024Q1','2025-06','formal_adverse_6m',.463,.391,'Red','debt_to_income_dti',.198,'Reviewed','No immediate action','No event',null],
  ['ALT-2025-0005','DEMO-000005','2006Q3','2025-06','formal_adverse_6m',.425,.391,'Red','current_interest_rate',.174,'Pending','','Unobserved',null],
  ['ALT-2025-0006','DEMO-000006','2012Q3','2025-06','early_deterioration_6m',.296,.118,'Amber','current_delinquency_status',.317,'Reviewed','Monitoring','30+ DPD',3],
  ['ALT-2025-0007','DEMO-000007','2016Q1','2025-06','early_deterioration_6m',.244,.118,'Amber','loan_age',.191,'In review','','Unobserved',null],
  ['ALT-2025-0008','DEMO-000008','2020Q3','2025-06','early_deterioration_6m',.211,.118,'Amber','original_combined_loan_to_value_ratio_cltv',.176,'Reviewed','Monitoring','No event',null],
  ['ALT-2025-0009','DEMO-000009','2022Q3','2025-06','early_deterioration_6m',.187,.118,'Amber','original_interest_rate',.159,'Pending','','Unobserved',null],
  ['ALT-2025-0010','DEMO-000010','2024Q3','2025-06','early_deterioration_6m',.151,.118,'Amber','debt_to_income_dti',.143,'Reviewed','Watchlist','30+ DPD',2],
  ['ALT-2025-0011','DEMO-000011','2008Q1','2025-07','formal_adverse_6m',.713,.391,'Red','current_delinquency_status',.403,'Reviewed','Priority follow-up','90+ DPD',1],
  ['ALT-2025-0012','DEMO-000012','2012Q1','2025-07','formal_adverse_6m',.518,.391,'Red','borrower_credit_score_at_origination',.221,'Pending','','Unobserved',null],
  ['ALT-2025-0013','DEMO-000013','2018Q3','2025-07','early_deterioration_6m',.267,.118,'Amber','current_delinquency_status',.299,'Reviewed','Monitoring','30+ DPD',3],
  ['ALT-2025-0014','DEMO-000014','2020Q1','2025-07','early_deterioration_6m',.193,.118,'Amber','loan_age',.164,'In review','','Unobserved',null],
  ['ALT-2025-0015','DEMO-000015','2024Q1','2025-07','early_deterioration_6m',.139,.118,'Amber','property_state',.121,'Reviewed','No immediate action','No event',null],
].map(([alertId, loanId, cohort, reportingMonth, target, riskScore, threshold, tier, topDriver, contribution, reviewStatus, decision, outcome, leadTimeMonths]) => ({
  alertId, loanId, cohort, reportingMonth, target, riskScore, threshold, tier, topDriver, contribution, reviewStatus, decision, outcome, leadTimeMonths, modelVersion: 'calibrated_xgboost_v01', dataVersion: 'fannie_panel_v01',
}));

export const driverLabel = (driver) => ({
  current_delinquency_status: 'Current delinquency status', original_interest_rate: 'Original interest rate', borrower_credit_score_at_origination: 'FICO at origination', debt_to_income_dti: 'Debt-to-income ratio', current_interest_rate: 'Current interest rate', loan_age: 'Loan age', original_combined_loan_to_value_ratio_cltv: 'Original CLTV', property_state: 'Property state',
}[driver] ?? driver);

export const initialAuditEntries = demoAlerts.filter((alert) => alert.reviewStatus === 'Reviewed').map((alert) => ({
  id: `AUD-${alert.alertId}`, alertId: alert.alertId, recordedAt: `${alert.reportingMonth}-05`, modelVersion: alert.modelVersion,
  tier: alert.tier, decision: alert.decision, actor: 'demo_reviewer', source: 'Seeded demonstration review',
}));
