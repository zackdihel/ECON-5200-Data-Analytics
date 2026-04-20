# Causal ML – DML and Causal Forests for Policy Evaluation

## Objective
Apply Double Machine Learning and Causal Forest methods to estimate the causal effect of 401(k) eligibility on household financial assets, and characterize treatment effect heterogeneity across the income distribution.

## Methodology
- Diagnosed and corrected three implementation bugs in a manual DML estimator: data leakage from same-fold training and prediction, missing treatment residualization, and an incorrect mean-based theta formula in place of the proper IV-style ratio
- Validated the corrected estimator on a simulated DGP with a known ATE of 5.0, confirming near-unbiased recovery
- Estimated the ATE of 401(k) eligibility on net total financial assets using the `doubleml` PLR framework with `LassoCV` (outcome) and `LogisticRegressionCV` (treatment) nuisance learners and 5-fold cross-fitting; identified and excluded `p401` as a bad control (downstream mediator) that was suppressing the true effect
- Conducted sensitivity analysis to bound robustness to unmeasured confounding at `cf_y = cf_d = 0.03`
- Fit a `CausalForestDML` (EconML) to generate individual-level CATE predictions with 95% confidence intervals
- Compared quartile-level subgroup DML to Causal Forest estimates to quantify how much heterogeneity coarse stratification misses

## Key Findings
| Metric | Value |
|---|---|
| DML ATE | $8,290 |
| 95% Confidence Interval | [$7,271, $9,308] |
| p-value | < 0.001 |
| Mean CATE – Q1 income | $3,014 |
| Mean CATE – Q4 income | $15,345 |
| Within- vs. between-quartile variance ratio | 2.7× |

401(k) eligibility causally increases net financial assets by approximately **$8,290**, an estimate robust to moderate unmeasured confounding. The Causal Forest revealed that income quartile alone is a coarse proxy for individual benefit — within-quartile variance was **2.7× larger** than between-quartile variance, meaning subgroup DML by income bracket systematically obscures the majority of treatment effect heterogeneity. By conditioning simultaneously on age, education, family structure, and homeownership, the Causal Forest surfaces high-response individuals across all income brackets, with practical implications for targeting policy outreach.