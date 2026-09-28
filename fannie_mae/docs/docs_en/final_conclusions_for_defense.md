# Final conclusions for the defence

1. On the independent OOT period, XGBoost reaches ROC-AUC 0.8943 and PR-AUC 0.2866 for `formal_adverse_6m`, compared with 0.8794 and 0.1879 for logistic regression.
2. For `early_deterioration_6m`, XGBoost reaches ROC-AUC 0.7310 and PR-AUC 0.0663; its advantage over logistic regression is 0.0056 and 0.0066.
3. Isotonic calibration reduces the logistic-regression Brier score from 0.021646 to 0.004320 for formal adverse and from 0.059429 to 0.022507 for early deterioration.
4. The top-1% Red policy identifies 50.09% of formal-adverse events at 24.29% precision and mean lead time of 2.467 months. The top-5% Amber policy has 8.69% precision, 18.59% recall, and 2.993 months of lead time.
5. In the horizon comparison, three months provide the strongest ranking and 12 months the longest lead time; six months provide the operational compromise between them.
6. In the analysed Q1 setting, 1% natural-rate train (622,812 and 609,823 records for the two outcomes) provides competitive OOT metrics. This is a computational reference for research retraining, not a universal data-volume requirement.
7. The Q1/Q3 explanation comparison gives SHAP rank agreement of 0.9962 and 0.9938, with top-ten overlap of 10 and 9. This supports internal explanation stability but does not replace an independent Freddie Mac validation.

The full interpretation and limitations are in sections 6.3–6.6 of [Chapter 6](chapters/06_results_discussion_chapter.md).
