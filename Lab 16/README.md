## Lab: High-Dimensional GDP Growth Forecasting with Regularized Regression

**Domain:** Development Economics · High-Dimensional Prediction · Regularisation Theory  
**Tools:** Python, Pandas, NumPy, Scikit-Learn (`RidgeCV`, `LassoCV`, `lasso_path`, `StandardScaler`, `train_test_split`), Matplotlib, `wbgapi`  
**Dataset:** World Bank World Development Indicators — 35+ indicators across trade, macroeconomics, education, infrastructure, health, finance, natural resources, agriculture, and governance for 120+ countries, 2013–2019

---

### Objective

To forecast 5-year average GDP per capita growth across 120+ countries using 50+ World Development Indicators, demonstrating that OLS overfits catastrophically in a high-dimensional cross-country panel and that Ridge and Lasso regularisation with cross-validated penalty selection recover out-of-sample predictive performance — while Lasso's additional sparsity exposes the critical distinction between predictive redundancy and economic irrelevance.

---

### Methodology

- **Live Data Ingestion via World Bank API (`wbgapi`):** Programmatically fetched 35+ World Development Indicators spanning eight development dimensions — trade openness, macroeconomic stability, educational attainment, infrastructure access, health outcomes, financial depth, natural resource dependence, agricultural structure, and institutional governance — for 120+ countries over 2013–2019. Constructed a cross-sectional panel with the 5-year average GDP per capita growth rate as the outcome, averaging predictors to mitigate single-year noise and align with the medium-run growth forecasting horizon.

- **Feature Standardisation (`StandardScaler`):** Applied zero-mean, unit-variance standardisation to all 50+ predictors before model fitting. This is a necessary precondition for regularised regression: the Ridge and Lasso penalty terms apply uniform shrinkage pressure across all coefficients, which is only economically interpretable when all features are on a comparable scale. Without standardisation, the penalty disproportionately shrinks coefficients on high-variance indicators — effectively making the regularisation a function of measurement units rather than signal content.

- **OLS Baseline — Demonstrating High-Dimensional Overfitting:** Fitted an unregularised OLS model on the full 50+ feature set. With a predictor-to-observation ratio approaching or exceeding one in several splits, OLS has sufficient degrees of freedom to memorise training-set idiosyncrasies — producing a high training R² that reflects interpolation of the 120-country sample rather than capture of generalisable growth dynamics. Evaluated on the held-out test set, the OLS model's R² collapsed — in some configurations going negative, indicating that the model is a worse predictor than the unconditional mean of the outcome. This is the high-dimensional overfitting failure mode in its most legible form.

- **Ridge Regression with Cross-Validated λ (`RidgeCV`):** Re-estimated the growth model with L2 regularisation, using `RidgeCV` to select the penalty parameter λ that minimises cross-validated prediction error over a log-spaced grid. Ridge applies a quadratic penalty to all coefficient magnitudes simultaneously — shrinking every predictor toward zero proportionally, with no predictor dropped entirely. In the cross-country growth context, where many WDI indicators are theoretically relevant but empirically correlated (e.g., infant mortality and education access), Ridge handles multicollinearity by distributing the explanatory credit across correlated predictors rather than amplifying unstable OLS estimates.

- **Lasso Regression with Cross-Validated λ (`LassoCV`) and Coefficient Path (`lasso_path`):** Fitted an L1-regularised model using `LassoCV`, which selects the penalty parameter that minimises CV error while driving a subset of coefficients to exact zero — performing simultaneous prediction and variable selection. Visualised the full **coefficient regularisation path** using `lasso_path`: as λ increases from zero (OLS) toward infinity (null model), coefficients are progressively set to zero in a sequence that reveals the model's implicit ranking of predictor importance under sparsity constraints. The path diagram identifies which WDI indicators enter the model first (highest marginal predictive value after controlling for all others) and which are zeroed immediately (redundant given the active set).

- **Train/Test Out-of-Sample Evaluation:** Split the cross-national panel into training and held-out test sets using `train_test_split`. All model selection — λ grid search, cross-validation, coefficient estimation — was performed exclusively on the training partition. Performance metrics (R², RMSE) were evaluated exclusively on the test partition, ensuring no look-ahead contamination of the out-of-sample benchmark.

---

### Key Findings

**OLS Overfitting Was Catastrophic in This Dimension**

With 50+ predictors and 120+ observations, OLS operated in a near-saturated regime in which the model had sufficient degrees of freedom to fit training-sample noise as if it were signal. The result — high training R², negative or near-zero test R² — is the clearest possible demonstration that in-sample fit is not a model quality metric in high-dimensional settings. A model worse than the unconditional mean is not merely imprecise; it is actively misleading as a forecasting tool, and any development economist relying on its country-level predictions would systematically misallocate analytical resources.

**Ridge Recovered Out-of-Sample Performance via Variance Compression**

The cross-validated Ridge model produced materially positive test R², confirming that the growth signal embedded in the WDI indicators is real and generalisable — it was OLS variance, not signal absence, that produced the out-of-sample failure. Ridge's coefficient path shows the smooth, proportional shrinkage of all predictors: no indicator is discarded, but all are compressed toward zero in proportion to their instability under resampling. This is the correct response to a setting where many predictors contain genuine but correlated information about growth outcomes.

**Lasso Achieved Comparable Predictive Performance with a Sparse Predictor Set**

Lasso's test R² approximated Ridge's while retaining only a fraction of the 50+ predictors — zeroing out indicators whose marginal predictive contribution, conditional on the retained set, was insufficient to justify the L1 penalty cost. This result has two distinct implications that must be interpreted carefully:

1. **Predictive redundancy is not economic irrelevance.** A coefficient zeroed by Lasso does not indicate that the underlying indicator has no effect on growth — it indicates that, given the other retained predictors, the zeroed indicator adds no independent forecast accuracy. In a development economics panel where infrastructure access, health outcomes, and income levels are structurally correlated, Lasso selects one representative from each correlated cluster and discards the rest as redundant *for prediction*. The discarded indicators may still be causally important; Lasso simply does not need them given the retained correlates.

2. **The Lasso path is an implicit importance ranking.** The sequence in which indicators enter the model as λ decreases from its maximum value is a data-driven ranking of marginal predictive contribution under sparsity. Indicators entering at high λ (low regularisation) — typically trade openness, human capital proxies, and institutional quality metrics — are the growth predictors most robust to competing specifications. This ranking is not a causal identification result, but it is a principled signal about which development dimensions dominate the 5-year growth forecast when the model is forced to be parsimonious.

**The Bias-Variance Tradeoff Across Three Estimators**

The OLS → Ridge → Lasso sequence across this lab traces the bias-variance frontier in a high-dimensional cross-country setting. OLS minimises bias but carries unbounded variance in near-saturated designs. Ridge introduces controlled bias via L2 shrinkage and substantially reduces variance. Lasso introduces structural sparsity — additional bias in the form of exact zero constraints — in exchange for the maximum variance reduction achievable through variable elimination. That Lasso and Ridge achieved similar test R² demonstrates that the dropped predictors contributed more variance than signal to OLS: their exclusion is not a loss of information but a correction of noise amplification.

---

### Economic Interpretation

This lab sits at the intersection of two distinct literatures: the empirical growth econometrics tradition, which has long grappled with model uncertainty over a large set of candidate growth determinants (Levine & Renelt, 1992; Sala-i-Martin, 1997), and the modern statistical learning literature on regularisation for high-dimensional prediction.

The regularisation approach does not resolve the causal identification problems that have occupied the growth empirics literature for three decades — OLS endogeneity, omitted country-level heterogeneity, and reverse causality between institutions and growth remain unaddressed. What it does resolve is the *predictive* problem: given a large WDI feature set and a modest cross-country sample, which estimation strategy produces the most reliable forecast of medium-run growth performance?

The answer — regularised regression with cross-validated penalty selection — is not surprising from a statistical learning perspective. But contextualising it within the growth empirics literature reframes the contribution: Lasso's implicit variable selection is a data-driven partial answer to the "which variables really matter for growth?" question that Sala-i-Martin's Bayesian model averaging literature asked three decades ago. The methodology has changed; the economic question has not.

---

*Part of ECON 5200: Applied Data Analytics in Economics*
