Fraud Detection Model Evaluation — Metrics That Matter
Objective: Rigorously evaluate a logistic regression fraud classifier on a severely imbalanced real-world dataset, demonstrating why accuracy alone is a misleading performance metric and how threshold selection can be operationalized under business capacity constraints.

Methodology

Dataset: Kaggle Credit Card Fraud Detection dataset — 284,807 European credit card transactions with PCA-anonymized features (V1–V28), transaction Amount, and a binary fraud label. Positive class frequency: ~0.172%.
Baseline audit: Constructed a naive all-negative classifier to expose the accuracy paradox — achieving 99.83% accuracy while detecting zero fraud cases.
Model training: Fit a logistic regression classifier using scikit-learn; evaluated predictions on a held-out test set.
Evaluation suite: Generated confusion matrices and full classification reports; computed ROC-AUC and Precision-Recall AUC to assess discriminative power on the minority class.
Threshold analysis: Swept decision thresholds across [0.01, 0.99] to identify the F1-optimal cutoff, demonstrating divergence from the naïve 0.5 default.
Capacity-constrained operating point: Applied a business rule limiting daily investigations to 500 cases; selected the highest threshold at which flagged volume remained within budget, then reported Recall and Precision at that operating point.


Key Findings
The naive baseline exposed the accuracy paradox clearly: a classifier that predicts "no fraud" on every transaction achieves 99.83% accuracy yet has zero practical value for a fraud team. Logistic regression achieved strong ROC-AUC performance and meaningful PR-AUC on the fraud class — a more honest signal on imbalanced data. The F1-optimal threshold differed materially from 0.5, confirming that default thresholds are poorly calibrated for rare-event detection. Under the 500-investigation capacity constraint, the model identified a business-viable operating point, surfacing a quantified Recall that directly informs the VP of Risk's expected fraud capture rate per day.